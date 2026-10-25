from datetime import date

from django.shortcuts import render

from db.database import fetch_all, fetch_one

# Список площадок (запрос 2 в sql/queries.sql).
VENUE_LIST_SQL = """
    SELECT id, name, address, capacity
    FROM venues
    ORDER BY capacity DESC
"""

VENUE_DETAIL_SQL = """
    SELECT id, name, address, capacity
    FROM venues
    WHERE id = ?
"""

# Сколько программ проходит на площадке в дату (запрос 6).
VENUE_PROGRAMS_ON_DATE_SQL = """
    SELECT COUNT(*) AS programs_count
    FROM programs
    WHERE venue_id = ?
      AND event_date = ?
"""

# Свободные площадки на дату с вместимостью не менее N (запрос 7).
AVAILABLE_VENUES_SQL = """
    SELECT id, name, address, capacity
    FROM venues
    WHERE capacity >= ?
      AND id NOT IN (
          SELECT venue_id
          FROM programs
          WHERE event_date = ?
      )
    ORDER BY capacity
"""


def venues(request):
    """Страница списка площадок."""
    context = {
        "venues": fetch_all(VENUE_LIST_SQL),
    }

    return render(request, "venues/venue_list.html", context)


def venue_detail(request, venue_id):
    """Страница площадки; для неизвестного id - ответ с кодом 404."""
    venue = fetch_one(VENUE_DETAIL_SQL, [venue_id])
    today = date.today()

    # Площадка свободна, если сегодня на ней нет ни одной программы.
    is_available = None
    if venue is not None:
        row = fetch_one(
            VENUE_PROGRAMS_ON_DATE_SQL,
            [venue_id, today.isoformat()],
        )
        is_available = row["programs_count"] == 0

    context = {
        "venue": venue,
        "is_available": is_available,
        "today": today,
    }

    return render(
        request,
        "venues/venue_detail.html",
        context,
        status=404 if venue is None else 200,
    )


def available_venues(request):
    """Подбор площадки: свободна в дату и вмещает нужное число зрителей.

    Значения приходят из GET-параметров формы, например
    /venues/available/?date=2026-11-20&capacity=500.
    Пока дата не выбрана, запрос к базе не выполняется.
    """
    date_value = request.GET.get("date", "").strip()
    capacity_value = request.GET.get("capacity", "").strip()

    errors = []
    event_date = None
    capacity = 0

    if date_value:
        try:
            event_date = date.fromisoformat(date_value)
        except ValueError:
            errors.append("Дата должна быть в формате ГГГГ-ММ-ДД.")

    if capacity_value:
        try:
            capacity = int(capacity_value)
        except ValueError:
            errors.append("Число зрителей должно быть целым числом.")
        else:
            if capacity < 0:
                errors.append("Число зрителей не может быть меньше 0.")

    venues_list = []
    searched = event_date is not None and not errors
    if searched:
        venues_list = fetch_all(
            AVAILABLE_VENUES_SQL,
            [capacity, event_date.isoformat()],
        )

    context = {
        "venues": venues_list,
        "date_value": date_value,
        "capacity_value": capacity_value,
        "event_date": event_date,
        "capacity": capacity,
        "errors": errors,
        "searched": searched,
    }

    return render(request, "venues/available.html", context)
