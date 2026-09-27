from __future__ import annotations

from datetime import date
from typing import Optional

from .programs import Program


class Ticket:
    """Билет на концертную программу."""

    def __init__(
            self,
            ticket_id: int,
            program: Program,
            seat: str,
            category: str,
            price: float,
            status: str = "sold",
    ) -> None:
        """Создать объект билета."""
        self.id = ticket_id
        self.program = program
        self.seat = seat
        self.category = category
        self.price = price
        self.status = status

    def is_active(self) -> bool:
        """Проверить, активен ли билет."""
        return self.status == "sold"

    def cancel(self) -> None:
        """Отменить билет (изменить его состояние)."""
        self.status = "cancelled"

    def __str__(self) -> str:
        """Вернуть строковое представление билета."""
        return (
            f"Билет на «{self.program.title}», "
            f"место {self.seat} ({self.category}), "
            f"{self.price} руб., статус: {self.status}"
        )

    @classmethod
    def from_data(
            cls,
            data: dict,
            programs: list[Program],
    ) -> Optional["Ticket"]:
        """Создать билет из данных с восстановлением связи."""
        program = next(
            (p for p in programs if p.id == data["program_id"]),
            None,
        )
        if program is None:
            return None
        return cls(
            ticket_id=data["id"],
            program=program,
            seat=data["seat"],
            category=data["category"],
            price=data["price"],
            status=data.get("status", "sold"),
        )

    def to_data(self) -> dict:
        """Преобразовать объект в словарь для сохранения."""
        return {
            "id": self.id,
            "program_id": self.program.id,
            "seat": self.seat,
            "category": self.category,
            "price": self.price,
            "status": self.status,
        }


def next_ticket_id(tickets: list[Ticket]) -> int:
    """Вернуть следующий свободный идентификатор билета."""
    if not tickets:
        return 1
    return max(ticket.id for ticket in tickets) + 1


def is_venue_available(
        programs: list[Program],
        venue_id: int,
        event_date: date,
) -> bool:
    """Проверить, свободна ли площадка на указанную дату."""
    date_iso = event_date.isoformat()
    for program in programs:
        same_venue = program.venue.id == venue_id
        same_date = program.event_date == date_iso
        if same_venue and same_date:
            return False
    return True


def get_booking_status(is_available: bool) -> str:
    """Вернуть текстовый статус доступности площадки.

    Функция перенесена из ПР1 без изменений.
    """
    if is_available:
        return "Площадка доступна для бронирования"
    return "Площадка уже занята"


def calculate_ticket_price(base_price: float, code: str) -> float:
    """Рассчитать стоимость билета с учётом промокода.

    Функция развивает сценарий из ПР1.
    """
    if code == "AUTUMN15":
        discount = 0.15
    elif code == "STUDENT":
        discount = 0.30
    else:
        discount = 0.0
    return round(base_price * (1 - discount), 2)


def create_ticket(
        tickets: list[Ticket],
        program: Program,
        seat: str,
        category: str,
        promo_code: str = "",
) -> Ticket:
    """Создать билет и добавить его в коллекцию."""
    price = calculate_ticket_price(program.base_price, promo_code)
    ticket = Ticket(
        next_ticket_id(tickets),
        program,
        seat,
        category,
        price,
    )
    tickets.append(ticket)
    return ticket


def find_ticket_by_id(
        tickets: list[Ticket],
        ticket_id: int,
) -> Optional[Ticket]:
    """Найти билет по идентификатору."""
    for ticket in tickets:
        if ticket.id == ticket_id:
            return ticket
    return None


def cancel_ticket(tickets: list[Ticket], ticket_id: int) -> bool:
    """Отменить билет по идентификатору.

    Билет не удаляется из коллекции — изменяется его состояние
    через метод cancel(). Это сохраняет историю продаж.
    """
    ticket = find_ticket_by_id(tickets, ticket_id)
    if ticket is None:
        return False
    ticket.cancel()
    return True


def filter_tickets_by_program(
        tickets: list[Ticket],
        program_id: int,
) -> list[Ticket]:
    """Отобрать билеты по идентификатору программы."""
    return [
        ticket for ticket in tickets
        if ticket.program.id == program_id
    ]


def count_active_tickets_by_program(
        tickets: list[Ticket],
        program_id: int,
) -> int:
    """Посчитать активные билеты на программу."""
    return sum(
        1 for ticket in tickets
        if ticket.program.id == program_id and ticket.is_active()
    )


def show_tickets(tickets: list[Ticket]) -> None:
    """Вывести список билетов."""
    if not tickets:
        print("Проданных билетов нет.")
        return
    print("--- Билеты ---")
    for ticket in tickets:
        print(f"[{ticket.id}] {ticket}")
