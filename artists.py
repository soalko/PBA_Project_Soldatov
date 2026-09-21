def _next_id(artists: list[dict]) -> int:
    """Вернуть следующий свободный идентификатор исполнителя."""
    if not artists:
        return 1
    return max(artist["id"] for artist in artists) + 1


def add_artist(
        artists: list[dict],
        name: str,
        country: str,
        genre: str
) -> dict:
    """Добавить исполнителя в список artists."""
    artist = {
        "id": _next_id(artists),
        "name": name,
        "country": country,
        "genre": genre,
    }
    artists.append(artist)
    return artist


def find_artist_by_id(
        artists: list[dict],
        artist_id: int
) -> dict | None:
    """Найти исполнителя по идентификатору."""
    for artist in artists:
        if artist["id"] == artist_id:
            return artist
    return None


def find_artists(artists: list[dict], query: str) -> list[dict]:
    """Найти исполнителей по подстроке имени."""
    query_lower = query.lower()
    return [
        artist for artist in artists
        if query_lower in artist["name"].lower()
    ]


def filter_artists_by_genre(
        artists: list[dict],
        genre: str
) -> list[dict]:
    """Отобрать исполнителей по жанру."""
    genre_lower = genre.lower()
    return [
        artist for artist in artists
        if artist["genre"].lower() == genre_lower
    ]
