from datetime import date

from django.shortcuts import render

from homepage.views import data_file
from models.tickets import is_venue_available
from models.venues import find_venue_by_id
from storage import load_artists, load_programs, load_venues


def venues(request):
    """Страница списка площадок."""
    venues_list = load_venues(data_file("venues.json"))

    context = {
        "venues": venues_list,
    }

    return render(request, "venues/venue_list.html", context)


def venue_detail(request, venue_id):
    """Страница площадки; для неизвестного id - ответ с кодом 404."""
    venues_list = load_venues(data_file("venues.json"))
    venue = find_venue_by_id(venues_list, venue_id)

    # Доступность определяет логика ПР3, шаблон только выводит результат.
    is_available = None
    if venue is not None:
        artists_list = load_artists(data_file("artists.json"))
        programs_list = load_programs(
            data_file("programs.json"),
            artists_list,
            venues_list,
        )
        is_available = is_venue_available(
            programs_list,
            venue.id,
            date.today(),
        )

    context = {
        "venue": venue,
        "is_available": is_available,
        "today": date.today(),
    }

    return render(
        request,
        "venues/venue_detail.html",
        context,
        status=404 if venue is None else 200,
    )
