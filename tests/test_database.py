import json
import sqlite3

import pytest

import db.database
from db import import_json
from db.database import BASE_DIR, create_schema, get_connection


@pytest.fixture
def empty_db(tmp_path, monkeypatch):
    """Пустая временная база со схемой из sql/schema.sql."""
    monkeypatch.setattr(db.database, "DB_PATH", tmp_path / "empty.sqlite")
    conn = get_connection()
    create_schema(conn)
    yield conn
    conn.close()


def table_names(conn):
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
    ).fetchall()
    return [row["name"] for row in rows]


def test_schema_creates_tables(empty_db):
    assert table_names(empty_db) == [
        "artists", "programs", "tickets", "venues",
    ]


def test_schema_can_be_executed_twice(empty_db):
    create_schema(empty_db)
    assert len(table_names(empty_db)) == 4


def test_foreign_keys_are_declared(empty_db):
    program_fk = empty_db.execute(
        "PRAGMA foreign_key_list(programs)"
    ).fetchall()
    assert {row["table"] for row in program_fk} == {"artists", "venues"}
    ticket_fk = empty_db.execute(
        "PRAGMA foreign_key_list(tickets)"
    ).fetchall()
    assert [row["table"] for row in ticket_fk] == ["programs"]


def test_connection_enables_foreign_keys(empty_db):
    assert empty_db.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    with pytest.raises(sqlite3.IntegrityError):
        empty_db.execute(
            "INSERT INTO programs VALUES "
            "(1, 'Без исполнителя', 999, 999, 'рок', '2026-12-01', 100)"
        )


def test_check_constraints(empty_db):
    with pytest.raises(sqlite3.IntegrityError):
        empty_db.execute(
            "INSERT INTO venues VALUES (1, 'Зал', 'Адрес', 0)"
        )


def test_rows_are_accessed_by_name(empty_db):
    empty_db.execute("INSERT INTO venues VALUES (1, 'Зал', NULL, 10)")
    row = empty_db.execute("SELECT name, address FROM venues").fetchone()
    assert row["name"] == "Зал"
    assert row["address"] is None


COUNT_SQL = {
    "artists": "SELECT COUNT(*) FROM artists",
    "venues": "SELECT COUNT(*) FROM venues",
    "programs": "SELECT COUNT(*) FROM programs",
    "tickets": "SELECT COUNT(*) FROM tickets",
}


def test_import_transfers_all_json_records(empty_db):
    counts = import_json.import_all(empty_db)
    for table, sql in COUNT_SQL.items():
        path = BASE_DIR / "data" / f"{table}.json"
        expected = len(json.loads(path.read_text(encoding="utf-8")))
        assert counts[table] == expected
        assert empty_db.execute(sql).fetchone()[0] == expected


def test_import_can_be_repeated(empty_db):
    first = import_json.import_all(empty_db)
    second = import_json.import_all(empty_db)
    assert first == second


def test_failed_import_is_rolled_back(empty_db, monkeypatch):
    empty_db.commit()

    def broken_tickets(conn):
        conn.execute(
            "INSERT INTO tickets VALUES (1, 999, 'A1', NULL, 100, 'sold')"
        )

    monkeypatch.setattr(import_json, "import_tickets", broken_tickets)
    with pytest.raises(sqlite3.IntegrityError):
        import_json.main()
    # Исполнители уже были вставлены, но rollback() отменил и их.
    assert empty_db.execute("SELECT COUNT(*) FROM artists").fetchone()[0] == 0


def read_queries():
    """Вернуть SQL-команды из sql/queries.sql без комментариев."""
    text = (BASE_DIR / "sql" / "queries.sql").read_text(encoding="utf-8")
    lines = [
        line for line in text.splitlines()
        if not line.lstrip().startswith(("--", "."))
    ]
    statements = "\n".join(lines).split(";")
    return [s.strip() for s in statements if s.strip()]


def test_queries_file_contains_required_kinds():
    queries = read_queries()
    assert len(queries) >= 10
    for keyword in ("WHERE", "JOIN", "COUNT(", "GROUP BY"):
        assert sum(keyword in q for q in queries) >= 2, keyword
    assert any("HAVING" in q for q in queries)


def test_all_queries_run_on_imported_data(empty_db):
    import_json.import_all(empty_db)
    for query in read_queries():
        empty_db.execute(query).fetchall()
