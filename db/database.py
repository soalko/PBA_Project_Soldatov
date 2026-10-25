"""Подключение к базе данных SQLite проекта.

Модуль не зависит от Django: его используют и скрипт импорта
db/import_json.py, и view-функции веб-приложения.
"""
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Файл базы данных и файл со схемой таблиц.
DB_PATH = BASE_DIR / "data" / "concerts.sqlite"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"


def get_connection():
    """Открыть соединение с базой данных проекта.

    row_factory = sqlite3.Row позволяет обращаться к полям строки
    по имени: row["name"] в Python и {{ row.name }} в шаблоне.
    PRAGMA foreign_keys = ON включает проверку внешних ключей:
    по умолчанию SQLite её не выполняет, и настройка действует
    только для текущего соединения.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_schema(conn):
    """Создать таблицы, выполнив все команды из sql/schema.sql."""
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(sql)


def fetch_all(sql, params=()):
    """Выполнить SELECT и вернуть список всех строк результата.

    Значения передаются отдельно от текста запроса через
    параметры ?, поэтому пользовательский ввод не может изменить
    сам SQL-запрос.
    """
    conn = get_connection()
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def fetch_one(sql, params=()):
    """Выполнить SELECT и вернуть первую строку или None."""
    conn = get_connection()
    try:
        return conn.execute(sql, params).fetchone()
    finally:
        conn.close()
