from datetime import date, timedelta

from models import Artist, Program, Venue
from models.programs import (
    add_program,
    filter_programs_by_genre,
    find_programs,
    remove_program,
)


def _make_artist():
    return Artist(1, "Оркестр «Камертон»", "Россия", "классика")


def _make_venue():
    return Venue(1, "Октябрьский", "СПб", 1500)


def test_program_creation():
    program = Program(
        1,
        "Симфония осени",
        _make_artist(),
        _make_venue(),
        "классика",
        "2026-11-20",
        2500.0,
    )
    assert program.id == 1
    assert program.title == "Симфония осени"
    assert program.artist.id == 1
    assert program.venue.id == 1


def test_program_str_contains_data():
    program = Program(
        1,
        "Симфония осени",
        _make_artist(),
        _make_venue(),
        "классика",
        "2026-11-20",
        2500.0,
    )
    text = str(program)
    assert "Симфония осени" in text
    assert "Оркестр «Камертон»" in text


def test_program_is_upcoming():
    future = (date.today() + timedelta(days=30)).isoformat()
    program = Program(
        1, "Симфония", _make_artist(), _make_venue(),
        "классика", future, 2500.0,
    )
    assert program.is_upcoming()


def test_program_validate_empty_title():
    result = Program.validate(
        "", _make_artist(), date.today() + timedelta(days=30),
    )
    assert result.startswith("Ошибка")


def test_program_validate_past_date():
    result = Program.validate(
        "Симфония", _make_artist(),
        date.today() - timedelta(days=1),
    )
    assert result.startswith("Ошибка")


def test_program_validate_success():
    result = Program.validate(
        "Симфония", _make_artist(),
        date.today() + timedelta(days=30),
    )
    assert result.startswith("Программа")


def test_add_program():
    programs = []
    add_program(
        programs, "Симфония осени",
        _make_artist(), _make_venue(),
        "классика", date(2026, 11, 20), 2500.0,
    )
    assert len(programs) == 1
    assert programs[0].id == 1


def test_find_programs_by_query():
    programs = []
    add_program(
        programs, "Симфония осени",
        _make_artist(), _make_venue(),
        "классика", date(2026, 11, 20), 2500.0,
    )
    add_program(
        programs, "Рок-фестиваль",
        _make_artist(), _make_venue(),
        "рок", date(2026, 12, 1), 1500.0,
    )
    found = find_programs(programs, "симфония")
    assert len(found) == 1


def test_filter_programs_by_genre():
    programs = []
    add_program(
        programs, "Симфония осени",
        _make_artist(), _make_venue(),
        "классика", date(2026, 11, 20), 2500.0,
    )
    add_program(
        programs, "Рок-фестиваль",
        _make_artist(), _make_venue(),
        "рок", date(2026, 12, 1), 1500.0,
    )
    filtered = filter_programs_by_genre(programs, "рок")
    assert len(filtered) == 1


def test_remove_program():
    programs = []
    add_program(
        programs, "Симфония осени",
        _make_artist(), _make_venue(),
        "классика", date(2026, 11, 20), 2500.0,
    )
    assert remove_program(programs, 1)
    assert len(programs) == 0
