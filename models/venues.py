from __future__ import annotations

from typing import Optional


class Venue:
    """Концертная площадка."""

    def __init__(
            self,
            venue_id: int,
            name: str,
            address: str,
            capacity: int,
    ) -> None:
        """Создать объект площадки."""
        self.id = venue_id
        self.name = name
        self.address = address
        self.capacity = capacity

    def is_suitable_for(self, people_count: int) -> bool:
        """Проверить, вмещает ли площадка указанное число зрителей."""
        return self.capacity >= people_count

    @staticmethod
    def validate_capacity(capacity: int) -> bool:
        """Проверить корректность вместимости."""
        return capacity > 0

    def __str__(self) -> str:
        """Вернуть строковое представление площадки."""
        return (
            f"{self.name}, {self.address}, "
            f"до {self.capacity} чел."
        )

    @classmethod
    def from_data(cls, data: dict) -> "Venue":
        """Создать площадку из набора данных."""
        return cls(
            venue_id=data["id"],
            name=data["name"],
            address=data["address"],
            capacity=data["capacity"],
        )

    def to_data(self) -> dict:
        """Преобразовать объект в словарь для сохранения."""
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "capacity": self.capacity,
        }


def next_venue_id(venues: list[Venue]) -> int:
    """Вернуть следующий свободный идентификатор площадки."""
    if not venues:
        return 1
    return max(venue.id for venue in venues) + 1


def add_venue(
        venues: list[Venue],
        name: str,
        address: str,
        capacity: int,
) -> Venue:
    """Добавить площадку в коллекцию и вернуть объект."""
    venue = Venue(next_venue_id(venues), name, address, capacity)
    venues.append(venue)
    return venue


def find_venue_by_id(
        venues: list[Venue],
        venue_id: int,
) -> Optional[Venue]:
    """Найти площадку по идентификатору."""
    for venue in venues:
        if venue.id == venue_id:
            return venue
    return None


def find_venues(venues: list[Venue], query: str) -> list[Venue]:
    """Найти площадки по подстроке названия."""
    query_lower = query.lower()
    return [
        venue for venue in venues
        if query_lower in venue.name.lower()
    ]


def check_venue_capacity(
        venues: list[Venue],
        venue_id: int,
        min_capacity: int,
) -> bool:
    """Проверить, вмещает ли площадка не меньше min_capacity."""
    venue = find_venue_by_id(venues, venue_id)
    if venue is None:
        return False
    return venue.is_suitable_for(min_capacity)


def filter_venues_by_capacity(
        venues: list[Venue],
        min_capacity: int,
) -> list[Venue]:
    """Отобрать площадки по минимальной вместимости."""
    return [
        venue for venue in venues
        if venue.is_suitable_for(min_capacity)
    ]


def sort_venues(venues: list[Venue]) -> list[Venue]:
    """Отсортировать площадки по вместимости."""
    return sorted(venues, key=lambda venue: venue.capacity)


def show_venues(venues: list[Venue]) -> None:
    """Вывести список площадок."""
    if not venues:
        print("Список площадок пуст.")
        return
    print("--- Площадки ---")
    for venue in venues:
        print(f"[{venue.id}] {venue}")
