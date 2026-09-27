from __future__ import annotations

from datetime import date
from typing import Optional

from .artists import Artist
from .venues import Venue


class Program:
    """Концертная программа."""

    def __init__(
            self,
            program_id: int,
            title: str,
            artist: Artist,
            venue: Venue,
            genre: str,
            event_date: str,
            base_price: float,
    ) -> None:
        """Создать объект концертной программы."""
        self.id = program_id
        self.title = title
        self.artist = artist
        self.venue = venue
        self.genre = genre
        self.event_date = event_date
        self.base_price = base_price

    def is_upcoming(self) -> bool:
        """Проверить, что дата концерта ещё не наступила."""
        return date.fromisoformat(self.event_date) > date.today()

    @staticmethod
    def validate(
            title: str,
            artist: Optional[Artist],
            event_day: date,
    ) -> str:
        """Проверить корректность данных новой программы.

        Функция развивает сценарий из ПР1: проверяет название,
        исполнителя и дату проведения.
        """
        if not title.strip():
            return "Ошибка: не указано название программы"
        if artist is None:
            return "Ошибка: не указан исполнитель"
        if event_day <= date.today():
            return "Ошибка: дата концерта должна быть в будущем"
        return f"Программа «{title}» успешно создана"

    def __str__(self) -> str:
        """Вернуть строковое представление программы."""
        return (
            f"«{self.title}» ({self.genre}) — "
            f"{self.artist.name}, {self.venue.name}, "
            f"{self.event_date}, {self.base_price} руб."
        )

    @classmethod
    def from_data(
            cls,
            data: dict,
            artists: list[Artist],
            venues: list[Venue],
    ) -> Optional["Program"]:
        """Создать программу из данных с восстановлением связей."""
        artist = next(
            (a for a in artists if a.id == data["artist_id"]),
            None,
        )
        venue = next(
            (v for v in venues if v.id == data["venue_id"]),
            None,
        )
        if artist is None or venue is None:
            return None
        return cls(
            program_id=data["id"],
            title=data["title"],
            artist=artist,
            venue=venue,
            genre=data["genre"],
            event_date=data["event_date"],
            base_price=data["base_price"],
        )

    def to_data(self) -> dict:
        """Преобразовать объект в словарь для сохранения."""
        return {
            "id": self.id,
            "title": self.title,
            "artist_id": self.artist.id,
            "venue_id": self.venue.id,
            "genre": self.genre,
            "event_date": self.event_date,
            "base_price": self.base_price,
        }


def next_program_id(programs: list[Program]) -> int:
    """Вернуть следующий свободный идентификатор программы."""
    if not programs:
        return 1
    return max(program.id for program in programs) + 1


def add_program(
        programs: list[Program],
        title: str,
        artist: Artist,
        venue: Venue,
        genre: str,
        event_date: date,
        base_price: float,
) -> Program:
    """Добавить концертную программу в коллекцию."""
    program = Program(
        next_program_id(programs),
        title,
        artist,
        venue,
        genre,
        event_date.isoformat(),
        base_price,
    )
    programs.append(program)
    return program


def find_program_by_id(
        programs: list[Program],
        program_id: int,
) -> Optional[Program]:
    """Найти программу по идентификатору."""
    for program in programs:
        if program.id == program_id:
            return program
    return None


def find_programs(
        programs: list[Program],
        query: str,
) -> list[Program]:
    """Найти программы по подстроке названия."""
    query_lower = query.lower()
    return [
        program for program in programs
        if query_lower in program.title.lower()
    ]


def filter_programs_by_genre(
        programs: list[Program],
        genre: str,
) -> list[Program]:
    """Отобрать программы по жанру."""
    genre_lower = genre.lower()
    return [
        program for program in programs
        if program.genre.lower() == genre_lower
    ]


def sort_programs_by_date(programs: list[Program]) -> list[Program]:
    """Отсортировать программы по дате проведения."""
    return sorted(programs, key=lambda program: program.event_date)


def remove_program(
        programs: list[Program],
        program_id: int,
) -> bool:
    """Удалить программу по идентификатору."""
    program = find_program_by_id(programs, program_id)
    if program is None:
        return False
    programs.remove(program)
    return True


def show_programs(programs: list[Program]) -> None:
    """Вывести список концертных программ."""
    if not programs:
        print("Список программ пуст.")
        return
    print("--- Концертные программы ---")
    for program in programs:
        print(f"[{program.id}] {program}")
