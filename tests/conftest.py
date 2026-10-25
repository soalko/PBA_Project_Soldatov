import os
import sqlite3
from datetime import date, timedelta

import django
import pytest
from django.test import Client
from django.test.utils import setup_test_environment

import db.database

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "concerts.settings")
django.setup()
# debug=False включает собственную страницу 404 вместо отладочной.
setup_test_environment(debug=False)

FUTURE = (date.today() + timedelta(days=30)).isoformat()
TODAY = date.today().isoformat()


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    """Временная база SQLite с небольшим набором данных.

    db.database.DB_PATH подменяется, поэтому view-функции и
    get_connection() работают с этой базой, а не с data/concerts.sqlite.
    """
    path = tmp_path / "test.sqlite"
    monkeypatch.setattr(db.database, "DB_PATH", path)

    conn = db.database.get_connection()
    db.database.create_schema(conn)
    conn.execute(
        "INSERT INTO artists VALUES (?, ?, ?, ?)",
        (1, "Оркестр «Камертон»", "Россия", "классика"),
    )
    conn.executemany(
        "INSERT INTO venues VALUES (?, ?, ?, ?)",
        [
            (1, "Октябрьский", "СПб", 1500),
            (2, "Крокус", "Москва", 6000),
        ],
    )
    conn.executemany(
        "INSERT INTO programs VALUES (?, ?, ?, ?, ?, ?, ?)",
        [
            (1, "Симфония осени", 1, 1, "классика", FUTURE, 2500.0),
            (2, "Вечер классики", 1, 2, "классика", TODAY, 1800.0),
        ],
    )
    conn.executemany(
        "INSERT INTO tickets VALUES (?, ?, ?, ?, ?, ?)",
        [
            (1, 1, "A12", "партер", 2125.0, "sold"),
            (2, 1, "B7", "балкон", 2500.0, "cancelled"),
        ],
    )
    conn.commit()
    conn.close()
    return path


@pytest.fixture
def client(test_db):
    """Тестовый HTTP-клиент, страницы которого читают временную базу."""
    return Client()


@pytest.fixture
def run_sql(test_db):
    """Выполнить изменяющую SQL-команду во временной базе."""
    def run(sql, params=()):
        conn = sqlite3.connect(test_db)
        conn.execute(sql, params)
        conn.commit()
        conn.close()
    return run
