from datetime import date

from models import Artist, Program, Ticket, Venue
from models.tickets import (
    calculate_ticket_price,
    cancel_ticket,
    create_ticket,
    get_booking_status,
    is_venue_available,
)


def _make_program() -> Program:
    artist = Artist(1, "Оркестр", "Россия", "классика")
    venue = Venue(1, "Октябрьский", "СПб", 1500)
    return Program(
        1, "Симфония осени", artist, venue,
        "классика", "2026-11-20", 2500.0,
    )


def test_ticket_creation_and_links():
    program = _make_program()
    ticket = Ticket(1, program, "A12", "партер", 2125.0)
    assert ticket.id == 1
    assert ticket.program is program
    assert ticket.seat == "A12"
    assert ticket.is_active()


def test_ticket_cancel_changes_state():
    program = _make_program()
    ticket = Ticket(1, program, "A12", "партер", 2125.0)
    ticket.cancel()
    assert ticket.status == "cancelled"
    assert not ticket.is_active()


def test_ticket_str_contains_data():
    program = _make_program()
    ticket = Ticket(1, program, "A12", "партер", 2125.0)
    text = str(ticket)
    assert "Симфония осени" in text
    assert "A12" in text


def test_ticket_from_data():
    program = _make_program()
    data = {
        "id": 1,
        "program_id": 1,
        "seat": "A12",
        "category": "партер",
        "price": 2125.0,
        "status": "sold",
    }
    ticket = Ticket.from_data(data, [program])
    assert ticket is not None
    assert ticket.program is program
    assert ticket.is_active()


def test_ticket_from_data_unknown_program():
    data = {
        "id": 1,
        "program_id": 99,
        "seat": "A12",
        "category": "партер",
        "price": 2125.0,
        "status": "sold",
    }
    assert Ticket.from_data(data, []) is None


def test_is_venue_available_empty():
    assert is_venue_available([], 1, date(2026, 11, 20))


def test_is_venue_available_busy():
    program = _make_program()
    assert not is_venue_available(
        [program], 1, date(2026, 11, 20),
    )


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
    program = _make_program()
    tickets = []
    ticket = create_ticket(
        tickets, program, "A12", "партер", "AUTUMN15",
    )
    assert len(tickets) == 1
    assert ticket.price == 2125.0


def test_cancel_ticket_changes_state():
    program = _make_program()
    tickets = []
    ticket = create_ticket(tickets, program, "A12", "партер")
    assert cancel_ticket(tickets, ticket.id)
    assert ticket.status == "cancelled"
    # билет остаётся в коллекции
    assert len(tickets) == 1
