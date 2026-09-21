from datetime import date

from models.programs import add_program
from models.tickets import (
    calculate_ticket_price,
    create_ticket,
    get_booking_status,
    is_venue_available,
)


def _make_programs():
    """Создать список программ с одной записью для тестов."""
    programs = []
    add_program(
        programs, "Симфония осени", 1, 1,
        "классика", date(2026, 11, 20), 2500.0
    )
    return programs


def test_is_venue_available_empty():
    programs = []
    assert is_venue_available(programs, 1, date(2026, 11, 20))


def test_is_venue_available_busy():
    programs = _make_programs()
    assert not is_venue_available(programs, 1, date(2026, 11, 20))


def test_get_booking_status_available():
    assert get_booking_status(True) == (
        "Площадка доступна для бронирования"
    )


def test_get_booking_status_busy():
    assert get_booking_status(False) == "Площадка уже занята"


def test_calculate_ticket_price_no_promo():
    assert calculate_ticket_price(1000.0, "") == 1000.0


def test_calculate_ticket_price_student():
    assert calculate_ticket_price(1000.0, "STUDENT") == 700.0


def test_create_ticket():
    programs = _make_programs()
    tickets = []
    ticket = create_ticket(
        tickets, programs, 1, "A12", "партер", "AUTUMN15"
    )
    assert ticket is not None
    assert len(tickets) == 1
    assert ticket["price"] == 2125.0


def test_create_ticket_unknown_program():
    programs = _make_programs()
    tickets = []
    ticket = create_ticket(
        tickets, programs, 999, "A12", "партер"
    )
    assert ticket is None
    assert len(tickets) == 0
