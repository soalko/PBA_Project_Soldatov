def _next_id(venues: list[dict]) -> int:
    """Вернуть следующий свободный идентификатор площадки."""
    if not venues:
        return 1
    return max(venue["id"] for venue in venues) + 1


def add_venue(
        venues: list[dict],
        name: str,
        address: str,
        capacity: int
) -> dict:
    """Добавить площадку в список venues."""
    venue = {
        "id": _next_id(venues),
        "name": name,
        "address": address,
        "capacity": capacity,
    }
    venues.append(venue)
    return venue


def find_venue_by_id(
        venues: list[dict],
        venue_id: int
) -> dict | None:
    """Найти площадку по идентификатору."""
    for venue in venues:
        if venue["id"] == venue_id:
            return venue
    return None


def find_venues(venues: list[dict], query: str) -> list[dict]:
    """Найти площадки по подстроке названия."""
    query_lower = query.lower()
    return [
        venue for venue in venues
        if query_lower in venue["name"].lower()
    ]


def check_venue_capacity(
        venues: list[dict],
        venue_id: int,
        min_capacity: int
) -> bool:
    """Проверить, вмещает ли площадка не меньше min_capacity."""
    venue = find_venue_by_id(venues, venue_id)
    if venue is None:
        return False
    return venue["capacity"] >= min_capacity


def filter_venues_by_capacity(
        venues: list[dict],
        min_capacity: int
) -> list[dict]:
    """Отобрать площадки по минимальной вместимости."""
    return [
        venue for venue in venues
        if venue["capacity"] >= min_capacity
    ]


def sort_venues(venues: list[dict]) -> list[dict]:
    """Отсортировать площадки по вместимости (по возрастанию)."""
    return sorted(venues, key=lambda venue: venue["capacity"])
