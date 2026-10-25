"""Перенос данных проекта из JSON-файлов в базу данных SQLite.

Запуск из корня проекта:
    python -m db.import_json

Скрипт можно запускать повторно: перед вставкой таблицы очищаются,
поэтому повторный запуск не приводит к ошибке занятого id.
"""
import json

from db.database import BASE_DIR, create_schema, get_connection

DATA_DIR = BASE_DIR / "data"


def load_json(filename):
    """Прочитать список записей из JSON-файла каталога data/."""
    with open(DATA_DIR / filename, encoding="utf-8") as file:
        return json.load(file)


def clear_tables(conn):
    """Удалить старые записи: сначала зависимые таблицы.

    Билеты ссылаются на программы, программы — на исполнителей
    и площадки, поэтому удалять в обратном порядке нельзя:
    внешний ключ не даст удалить запись, на которую есть ссылка.
    """
    conn.execute("DELETE FROM tickets")
    conn.execute("DELETE FROM programs")
    conn.execute("DELETE FROM venues")
    conn.execute("DELETE FROM artists")


def import_artists(conn):
    artists = load_json("artists.json")
    conn.executemany(
        "INSERT INTO artists (id, name, country, genre) "
        "VALUES (?, ?, ?, ?)",
        [
            (a["id"], a["name"], a["country"], a["genre"])
            for a in artists
        ],
    )
    return len(artists)


def import_venues(conn):
    venues = load_json("venues.json")
    conn.executemany(
        "INSERT INTO venues (id, name, address, capacity) "
        "VALUES (?, ?, ?, ?)",
        [
            (v["id"], v["name"], v["address"], v["capacity"])
            for v in venues
        ],
    )
    return len(venues)


def import_programs(conn):
    programs = load_json("programs.json")
    conn.executemany(
        "INSERT INTO programs "
        "(id, title, artist_id, venue_id, genre, event_date, base_price) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        [
            (
                p["id"],
                p["title"],
                p["artist_id"],
                p["venue_id"],
                p["genre"],
                p["event_date"],
                p["base_price"],
            )
            for p in programs
        ],
    )
    return len(programs)


def import_tickets(conn):
    tickets = load_json("tickets.json")
    conn.executemany(
        "INSERT INTO tickets "
        "(id, program_id, seat, category, price, status) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        [
            (
                t["id"],
                t["program_id"],
                t["seat"],
                t["category"],
                t["price"],
                t.get("status", "sold"),
            )
            for t in tickets
        ],
    )
    return len(tickets)


def import_all(conn):
    """Перенести все данные; вернуть число записей по таблицам.

    Порядок важен из-за внешних ключей: программа ссылается на
    исполнителя и площадку, билет — на программу, поэтому
    «родительские» таблицы заполняются раньше.
    """
    clear_tables(conn)
    return {
        "artists": import_artists(conn),
        "venues": import_venues(conn),
        "programs": import_programs(conn),
        "tickets": import_tickets(conn),
    }


def main():
    conn = get_connection()
    try:
        create_schema(conn)
        counts = import_all(conn)
        conn.commit()
    except Exception:
        # Ошибка в любой записи отменяет весь импорт целиком.
        conn.rollback()
        raise
    finally:
        conn.close()
    for table, count in counts.items():
        print(f"{table}: {count}")


if __name__ == "__main__":
    main()
