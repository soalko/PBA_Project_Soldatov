from __future__ import annotations

from typing import Optional


class Artist:
    """Исполнитель концертной программы."""

    def __init__(
            self,
            artist_id: int,
            name: str,
            country: str,
            genre: str,
    ) -> None:
        """Создать объект исполнителя."""
        self.id = artist_id
        self.name = name
        self.country = country
        self.genre = genre

    def __str__(self) -> str:
        """Вернуть строковое представление исполнителя."""
        return f"{self.name} ({self.genre}, {self.country})"

    @classmethod
    def from_data(cls, data: dict) -> "Artist":
        """Создать исполнителя из набора данных."""
        return cls(
            artist_id=data["id"],
            name=data["name"],
            country=data["country"],
            genre=data["genre"],
        )

    def to_data(self) -> dict:
        """Преобразовать объект в словарь для сохранения."""
        return {
            "id": self.id,
            "name": self.name,
            "country": self.country,
            "genre": self.genre,
        }


def next_artist_id(artists: list[Artist]) -> int:
    """Вернуть следующий свободный идентификатор исполнителя."""
    if not artists:
        return 1
    return max(artist.id for artist in artists) + 1


def add_artist(
        artists: list[Artist],
        name: str,
        country: str,
        genre: str,
) -> Artist:
    """Добавить исполнителя в коллекцию и вернуть объект."""
    artist = Artist(next_artist_id(artists), name, country, genre)
    artists.append(artist)
    return artist


def find_artist_by_id(
        artists: list[Artist],
        artist_id: int,
) -> Optional[Artist]:
    """Найти исполнителя по идентификатору."""
    for artist in artists:
        if artist.id == artist_id:
            return artist
    return None


def find_artists(
        artists: list[Artist],
        query: str,
) -> list[Artist]:
    """Найти исполнителей по подстроке имени."""
    query_lower = query.lower()
    return [
        artist for artist in artists
        if query_lower in artist.name.lower()
    ]


def filter_artists_by_genre(
        artists: list[Artist],
        genre: str,
) -> list[Artist]:
    """Отобрать исполнителей по жанру."""
    genre_lower = genre.lower()
    return [
        artist for artist in artists
        if artist.genre.lower() == genre_lower
    ]


def show_artists(artists: list[Artist]) -> None:
    """Вывести список исполнителей."""
    if not artists:
        print("Список исполнителей пуст.")
        return
    print("--- Исполнители ---")
    for artist in artists:
        print(f"[{artist.id}] {artist}")
