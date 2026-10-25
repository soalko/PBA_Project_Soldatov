from django.shortcuts import render

from db.database import fetch_all, fetch_one

# Билеты с программой и площадкой (запрос 10).
# is_active = 1 для проданного билета — правило Ticket.is_active() ПР3.
TICKET_LIST_SQL = """
    SELECT tickets.id,
           tickets.seat,
           tickets.status = 'sold' AS is_active,
           programs.title AS program_title,
           strftime('%d.%m.%Y', programs.event_date) AS event_day,
           venues.name AS venue_name
    FROM tickets
    JOIN programs ON tickets.program_id = programs.id
    JOIN venues ON programs.venue_id = venues.id
    ORDER BY tickets.id
"""

# Полная информация о билете из четырёх таблиц (запрос 11).
TICKET_DETAIL_SQL = """
    SELECT tickets.id,
           tickets.seat,
           tickets.category,
           tickets.price,
           tickets.status = 'sold' AS is_active,
           programs.id AS program_id,
           programs.title AS program_title,
           strftime('%d.%m.%Y', programs.event_date) AS event_day,
           artists.name AS artist_name,
           venues.name AS venue_name
    FROM tickets
    JOIN programs ON tickets.program_id = programs.id
    JOIN artists ON programs.artist_id = artists.id
    JOIN venues ON programs.venue_id = venues.id
    WHERE tickets.id = ?
"""

# Итоги продаж по активным билетам (запрос 12).
SALES_SUMMARY_SQL = """
    SELECT COUNT(*) AS tickets_sold,
           SUM(price) AS revenue,
           ROUND(AVG(price), 2) AS average_price
    FROM tickets
    WHERE status = 'sold'
"""

# Количество программ и диапазон цен (запрос 13).
PRICE_SUMMARY_SQL = """
    SELECT COUNT(*) AS programs_count,
           MIN(base_price) AS min_price,
           MAX(base_price) AS max_price
    FROM programs
"""

# Продажи по каждой программе, включая программы без продаж (запрос 15).
SALES_BY_PROGRAM_SQL = """
    SELECT programs.title,
           COUNT(tickets.id) AS tickets_sold,
           COALESCE(SUM(tickets.price), 0.0) AS revenue
    FROM programs
    LEFT JOIN tickets
           ON tickets.program_id = programs.id
          AND tickets.status = 'sold'
    GROUP BY programs.id, programs.title
    ORDER BY tickets_sold DESC, programs.title
"""

# Количество программ на каждой площадке (запрос 16).
PROGRAMS_BY_VENUE_SQL = """
    SELECT venues.name,
           COUNT(programs.id) AS programs_count
    FROM venues
    LEFT JOIN programs ON programs.venue_id = venues.id
    GROUP BY venues.id, venues.name
    ORDER BY programs_count DESC, venues.name
"""

# Число программ и средняя цена по жанрам (запрос 17).
PROGRAMS_BY_GENRE_SQL = """
    SELECT genre,
           COUNT(*) AS programs_count,
           ROUND(AVG(base_price), 2) AS average_price
    FROM programs
    GROUP BY genre
    ORDER BY programs_count DESC, genre
"""

# Программы, на которые продано не менее N билетов (запрос 18).
POPULAR_PROGRAMS_SQL = """
    SELECT programs.title,
           COUNT(tickets.id) AS tickets_sold
    FROM programs
    JOIN tickets ON tickets.program_id = programs.id
    WHERE tickets.status = 'sold'
    GROUP BY programs.id, programs.title
    HAVING COUNT(tickets.id) >= ?
    ORDER BY tickets_sold DESC, programs.title
"""

DEFAULT_MIN_SOLD = 2


def tickets(request):
    """Страница списка билетов."""
    context = {
        "tickets": fetch_all(TICKET_LIST_SQL),
    }

    return render(request, "tickets/ticket_list.html", context)


def ticket_detail(request, ticket_id):
    """Страница билета; для неизвестного id - ответ с кодом 404."""
    ticket = fetch_one(TICKET_DETAIL_SQL, [ticket_id])

    context = {
        "ticket": ticket,
    }

    return render(
        request,
        "tickets/ticket_detail.html",
        context,
        status=404 if ticket is None else 200,
    )


def statistics(request):
    """Статистика продаж: агрегатные запросы и группировка.

    Порог «популярной» программы задаётся параметром ?min_sold=N
    и передаётся в условие HAVING как параметр запроса.
    """
    error = None
    min_sold = DEFAULT_MIN_SOLD
    min_sold_value = request.GET.get("min_sold", "").strip()
    if min_sold_value:
        try:
            min_sold = int(min_sold_value)
        except ValueError:
            error = "Порог должен быть целым числом."
            min_sold = DEFAULT_MIN_SOLD
        else:
            if min_sold < 1:
                error = "Порог должен быть не меньше 1."
                min_sold = DEFAULT_MIN_SOLD

    context = {
        "sales": fetch_one(SALES_SUMMARY_SQL),
        "prices": fetch_one(PRICE_SUMMARY_SQL),
        "by_program": fetch_all(SALES_BY_PROGRAM_SQL),
        "by_venue": fetch_all(PROGRAMS_BY_VENUE_SQL),
        "by_genre": fetch_all(PROGRAMS_BY_GENRE_SQL),
        "popular": fetch_all(POPULAR_PROGRAMS_SQL, [min_sold]),
        "min_sold": min_sold,
        "error": error,
    }

    return render(request, "tickets/statistics.html", context)
