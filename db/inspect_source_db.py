"""Инспекция исходной базы ПР7 перед переносом данных в Django ORM.

Скрипт только читает базу data/concerts.sqlite: выводит таблицы,
столбцы и количество записей, а также проверяет, что внешние ключи
ссылаются на существующие записи.

Запуск из корня проекта:
    python db/inspect_source_db.py
"""
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_DB = BASE_DIR / "data" / "concerts.sqlite"

# Записи, у которых внешний ключ указывает на несуществующую строку.
# LEFT JOIN оставляет такие записи, а у «родителя» будет NULL.
BROKEN_LINKS_SQL = {
    "programs.artist_id": """
        SELECT COUNT(*) FROM programs
        LEFT JOIN artists ON programs.artist_id = artists.id
        WHERE artists.id IS NULL
    """,
    "programs.venue_id": """
        SELECT COUNT(*) FROM programs
        LEFT JOIN venues ON programs.venue_id = venues.id
        WHERE venues.id IS NULL
    """,
    "tickets.program_id": """
        SELECT COUNT(*) FROM tickets
        LEFT JOIN programs ON tickets.program_id = programs.id
        WHERE programs.id IS NULL
    """,
}


def open_read_only(path):
    """Открыть базу только на чтение: исходные данные не изменятся."""
    if not path.exists():
        raise FileNotFoundError(f"Исходная база не найдена: {path}")
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def main():
    with open_read_only(SOURCE_DB) as connection:
        tables = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        ).fetchall()

        for (table_name,) in tables:
            print(f"\nТаблица: {table_name}")
            columns = connection.execute(
                f'PRAGMA table_info("{table_name}")'
            ).fetchall()
            for column in columns:
                print(
                    f"  {column['name']}: {column['type']}, "
                    f"NOT NULL={column['notnull']}, "
                    f"PRIMARY KEY={column['pk']}"
                )
            count = connection.execute(
                f'SELECT COUNT(*) FROM "{table_name}"'
            ).fetchone()[0]
            print(f"  Количество записей: {count}")

        print("\nПроверка внешних ключей:")
        for link, sql in BROKEN_LINKS_SQL.items():
            broken = connection.execute(sql).fetchone()[0]
            print(f"  {link}: битых ссылок {broken}")


if __name__ == "__main__":
    main()
