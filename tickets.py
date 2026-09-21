from datetime import date

from programs import find_program_by_id


def is_venue_available(
        programs: list[dict],
        venue_id: int,
        event_date: date
) -> bool:
    """Проверить, свободна ли площадка на указанную дату."""
    date_iso = event_date.isoformat()
    for program in programs:
        same_venue = program["venue_id"] == venue_id
        same_date = program["event_date"] == date_iso
        if same_venue and same_date:
            return False
    return True


def get_booking_status(is_available: bool) -> str:
    """Вернуть текстовый статус доступности площадки."""
    if is_available:
        return "Площадка доступна для бронирования"
    return "Площадка уже занята"


def calculate_ticket_price(base_price: float, code: str) -> float:
    """Рассчитать стоимость билета с учётом промокода."""
    if code == "AUTUMN15":
        discount = 0.15
    elif code == "STUDENT":
        discount = 0.30
    else:
        discount = 0.0
    return round(base_price * (1 - discount), 2)


def _next_id(tickets: list[dict]) -> int:
    """Вернуть следующий свободный идентификатор билета."""
    if not tickets:
        return 1
    return max(ticket["id"] for ticket in tickets) + 1


def create_ticket(
        tickets: list[dict],
        programs: list[dict],
        program_id: int,
        seat: str,
        category: str,
        promo_code: str = ""
) -> dict | None:
    """Создать билет на концертную программу."""
    program = find_program_by_id(programs, program_id)
    if program is None:
        return None
    price = calculate_ticket_price(program["base_price"], promo_code)
    ticket = {
        "id": _next_id(tickets),
        "program_id": program_id,
        "seat": seat,
        "category": category,
        "price": price,
        "status": "sold",
    }
    tickets.append(ticket)
    return ticket


def cancel_ticket(tickets: list[dict], ticket_id: int) -> bool:
    """Отменить (удалить) билет по идентификатору."""
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            tickets.remove(ticket)
            return True
    return False


def filter_tickets_by_program(
        tickets: list[dict],
        program_id: int
) -> list[dict]:
    """Отобрать билеты по идентификатору программы."""
    return [
        ticket for ticket in tickets
        if ticket["program_id"] == program_id
    ]


def count_tickets_by_program(
        tickets: list[dict],
        program_id: int
) -> int:
    """Посчитать количество проданных билетов на программу."""
    return len(filter_tickets_by_program(tickets, program_id))
