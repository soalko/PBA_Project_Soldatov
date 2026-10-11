from datetime import date

from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import escape

from homepage.views import data_file, page
from models.tickets import is_venue_available
from models.venues import find_venue_by_id
from storage import load_artists, load_programs, load_venues


def venues(request):
    """Страница списка площадок."""
    items = ""
    for venue in load_venues(data_file("venues.json")):
        url = reverse("venue_detail", args=[venue.id])
        items += f"""
        <li class="list-group-item d-flex justify-content-between
                   align-items-center gap-2">
            <a href="{url}">{escape(venue.name)}</a>
            <span class="badge bg-secondary">
                вместимость {venue.capacity} мест
            </span>
        </li>
        """
    if not items:
        items = '<li class="list-group-item">Список площадок пуст</li>'
    content = f"""
    <h1>Площадки</h1>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page("Площадки", content))


def venue_detail(request, venue_id):
    """Страница площадки; для неизвестного id - ответ с кодом 404."""
    venues_list = load_venues(data_file("venues.json"))
    venue = find_venue_by_id(venues_list, venue_id)

    if venue is None:
        content = f"""
        <h1 class="text-danger">Площадка не найдена</h1>
        <a href="{reverse('venues')}" class="btn btn-outline-secondary">
            ← к списку площадок
        </a>
        """
        return HttpResponse(
            page("Площадка не найдена", content),
            status=404,
        )

    artists_list = load_artists(data_file("artists.json"))
    programs_list = load_programs(
        data_file("programs.json"),
        artists_list,
        venues_list,
    )
    available = is_venue_available(
        programs_list,
        venue.id,
        date.today(),
    )
    status = "свободна" if available else "занята"
    badge = "bg-success" if available else "bg-danger"

    content = f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">{escape(venue.name)}</h5>
            <p class="card-text">
                <strong>ID:</strong> {venue.id}
            </p>
            <p class="card-text">
                <strong>Адрес:</strong> {escape(venue.address)}
            </p>
            <p class="card-text">
                <strong>Вместимость:</strong> {venue.capacity} мест
            </p>
            <p class="card-text">
                Доступность на текущую дату:
                <span class="badge {badge}">{status}</span>
            </p>
            <a href="{reverse('venues')}"
               class="btn btn-outline-secondary">
                ← к списку площадок
            </a>
        </div>
    </div>
    """
    return HttpResponse(page(venue.name, content), status=200)
