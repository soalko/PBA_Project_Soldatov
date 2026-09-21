from datetime import date, timedelta

from models.programs import (
    add_program,
    check_program_creation,
    filter_programs_by_genre,
    find_programs,
    remove_program,
)


def test_add_program():
    programs = []
    add_program(
        programs, "Симфония осени", 1, 1,
        "классика", date(2026, 11, 20), 2500.0
    )
    assert len(programs) == 1
    assert programs[0]["title"] == "Симфония осени"
    assert programs[0]["id"] == 1


def test_find_programs_by_query():
    programs = []
    add_program(
        programs, "Симфония осени", 1, 1,
        "классика", date(2026, 11, 20), 2500.0
    )
    add_program(
        programs, "Рок-фестиваль", 2, 2,
        "рок", date(2026, 12, 1), 1500.0
    )
    found = find_programs(programs, "симфония")
    assert len(found) == 1
    assert found[0]["title"] == "Симфония осени"


def test_filter_programs_by_genre():
    programs = []
    add_program(
        programs, "Симфония осени", 1, 1,
        "классика", date(2026, 11, 20), 2500.0
    )
    add_program(
        programs, "Рок-фестиваль", 2, 2,
        "рок", date(2026, 12, 1), 1500.0
    )
    filtered = filter_programs_by_genre(programs, "рок")
    assert len(filtered) == 1
    assert filtered[0]["genre"] == "рок"


def test_check_program_creation_empty_title():
    result = check_program_creation(
        "", 1, date.today() + timedelta(days=30)
    )
    assert result.startswith("Ошибка")


def test_check_program_creation_past_date():
    result = check_program_creation(
        "Симфония осени", 1, date.today() - timedelta(days=1)
    )
    assert result.startswith("Ошибка")


def test_remove_program():
    programs = []
    add_program(
        programs, "Симфония осени", 1, 1,
        "классика", date(2026, 11, 20), 2500.0
    )
    assert remove_program(programs, 1)
    assert len(programs) == 0
