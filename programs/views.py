from django.shortcuts import render

from db.database import fetch_all, fetch_one

# Афиша: программы с исполнителем и площадкой (запрос 8).
# is_upcoming = 1, если дата программы ещё не наступила —
# то же правило, что в методе Program.is_upcoming() из ПР3.
PROGRAM_LIST_SQL = """
    SELECT programs.id,
           programs.title,
           strftime('%d.%m.%Y', programs.event_date) AS event_day,
           programs.event_date > date('now', 'localtime') AS is_upcoming,
           artists.name AS artist_name,
           venues.name AS venue_name
    FROM programs
    JOIN artists ON programs.artist_id = artists.id
    JOIN venues ON programs.venue_id = venues.id
    ORDER BY programs.event_date
"""

PROGRAM_DETAIL_SQL = """
    SELECT programs.id,
           programs.title,
           programs.genre,
           programs.base_price,
           strftime('%d.%m.%Y', programs.event_date) AS event_day,
           programs.event_date > date('now', 'localtime') AS is_upcoming,
           artists.id AS artist_id,
           artists.name AS artist_name,
           venues.id AS venue_id,
           venues.name AS venue_name
    FROM programs
    JOIN artists ON programs.artist_id = artists.id
    JOIN venues ON programs.venue_id = venues.id
    WHERE programs.id = ?
"""

# Количество активных билетов на программу (запрос 14).
PROGRAM_SOLD_SQL = """
    SELECT COUNT(*) AS sold
    FROM tickets
    WHERE program_id = ?
      AND status = 'sold'
"""


def programs(request):
    """Страница списка концертных программ, упорядоченных по дате."""
    context = {
        "programs": fetch_all(PROGRAM_LIST_SQL),
    }

    return render(request, "programs/program_list.html", context)


def program_detail(request, program_id):
    """Страница программы; для неизвестного id - ответ с кодом 404."""
    program = fetch_one(PROGRAM_DETAIL_SQL, [program_id])

    sold = 0
    if program is not None:
        sold = fetch_one(PROGRAM_SOLD_SQL, [program_id])["sold"]

    context = {
        "program": program,
        "sold": sold,
    }

    return render(
        request,
        "programs/program_detail.html",
        context,
        status=404 if program is None else 200,
    )
