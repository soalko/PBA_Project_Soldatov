from models import Artist
from models.artists import (
    add_artist,
    filter_artists_by_genre,
    find_artist_by_id,
    find_artists,
)


def test_artist_creation():
    artist = Artist(1, "Оркестр «Камертон»", "Россия", "классика")
    assert artist.id == 1
    assert artist.name == "Оркестр «Камертон»"
    assert artist.country == "Россия"
    assert artist.genre == "классика"


def test_artist_str():
    artist = Artist(1, "Оркестр «Камертон»", "Россия", "классика")
    assert str(artist) == "Оркестр «Камертон» (классика, Россия)"


def test_artist_from_data():
    data = {
        "id": 3,
        "name": "Группа «Северный ветер»",
        "country": "Россия",
        "genre": "рок",
    }
    artist = Artist.from_data(data)
    assert artist.id == 3
    assert artist.name == "Группа «Северный ветер»"


def test_add_artist():
    artists = []
    artist = add_artist(artists, "Оркестр", "Россия", "классика")
    assert len(artists) == 1
    assert artist.id == 1
    assert artists[0] is artist


def test_find_artist_by_id():
    artists = []
    add_artist(artists, "Оркестр", "Россия", "классика")
    add_artist(artists, "Рок-группа", "Россия", "рок")
    found = find_artist_by_id(artists, 2)
    assert found is not None
    assert found.name == "Рок-группа"


def test_find_artists_by_query():
    artists = []
    add_artist(artists, "Оркестр «Камертон»", "Россия", "классика")
    add_artist(artists, "Рок-группа", "Россия", "рок")
    found = find_artists(artists, "камертон")
    assert len(found) == 1
    assert found[0].name == "Оркестр «Камертон»"


def test_filter_artists_by_genre():
    artists = []
    add_artist(artists, "Оркестр", "Россия", "классика")
    add_artist(artists, "Рок-группа", "Россия", "рок")
    filtered = filter_artists_by_genre(artists, "рок")
    assert len(filtered) == 1
    assert filtered[0].genre == "рок"
