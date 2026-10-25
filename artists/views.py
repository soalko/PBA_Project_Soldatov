from django.shortcuts import render

from db.database import fetch_all, fetch_one

# Список исполнителей (запрос 1 в sql/queries.sql).
ARTIST_LIST_SQL = """
    SELECT id, name, country, genre
    FROM artists
    ORDER BY name
"""

# Жанры без повторов для фильтра (запрос 3).
GENRE_LIST_SQL = """
    SELECT DISTINCT genre
    FROM artists
    ORDER BY genre
"""

# Исполнители выбранного жанра (запрос 4).
ARTISTS_BY_GENRE_SQL = """
    SELECT id, name, country, genre
    FROM artists
    WHERE genre = ?
    ORDER BY name
"""

ARTIST_DETAIL_SQL = """
    SELECT id, name, country, genre
    FROM artists
    WHERE id = ?
"""

# Программы исполнителя с площадками (запрос 9).
ARTIST_PROGRAMS_SQL = """
    SELECT programs.id,
           programs.title,
           strftime('%d.%m.%Y', programs.event_date) AS event_day,
           venues.name AS venue_name
    FROM programs
    JOIN venues ON programs.venue_id = venues.id
    WHERE programs.artist_id = ?
    ORDER BY programs.event_date
"""


def artists(request):
    """Список исполнителей; ?genre=... оставляет только один жанр."""
    genre = request.GET.get("genre", "").strip()

    if genre:
        artists_list = fetch_all(ARTISTS_BY_GENRE_SQL, [genre])
    else:
        artists_list = fetch_all(ARTIST_LIST_SQL)

    context = {
        "artists": artists_list,
        "genres": fetch_all(GENRE_LIST_SQL),
        "selected_genre": genre,
    }

    return render(request, "artists/artist_list.html", context)


def artist_detail(request, artist_id):
    """Страница исполнителя; для неизвестного id - ответ с кодом 404."""
    artist = fetch_one(ARTIST_DETAIL_SQL, [artist_id])

    programs_list = []
    if artist is not None:
        programs_list = fetch_all(ARTIST_PROGRAMS_SQL, [artist_id])

    context = {
        "artist": artist,
        "programs": programs_list,
    }

    return render(
        request,
        "artists/artist_detail.html",
        context,
        status=404 if artist is None else 200,
    )
