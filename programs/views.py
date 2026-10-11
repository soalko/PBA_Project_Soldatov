from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import escape

from homepage.views import data_file, page
from models.programs import find_program_by_id, sort_programs_by_date
from models.tickets import count_active_tickets_by_program
from storage import (
    load_artists,
    load_programs,
    load_tickets,
    load_venues,
)


def programs(request):
    """Страница списка концертных программ, упорядоченных по дате."""
    artists_list = load_artists(data_file("artists.json"))
    venues_list = load_venues(data_file("venues.json"))
    programs_list = load_programs(
        data_file("programs.json"),
        artists_list,
        venues_list,
    )

    items = ""
    for program in sort_programs_by_date(programs_list):
        url = reverse("program_detail", args=[program.id])
        status = "предстоит" if program.is_upcoming() else "прошла"
        badge = "bg-success" if program.is_upcoming() else "bg-secondary"
        items += f"""
        <li class="list-group-item d-flex justify-content-between
                   align-items-center gap-2">
            <a href="{url}">
                {escape(program.title)} – {program.event_date}
            </a>
            <span class="badge {badge}">{status}</span>
        </li>
        """
    if not items:
        items = '<li class="list-group-item">Список программ пуст</li>'
    content = f"""
    <h1>Концертные программы</h1>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page("Концертные программы", content))


def program_detail(request, program_id):
    """Страница программы; для неизвестного id - ответ с кодом 404."""
    artists_list = load_artists(data_file("artists.json"))
    venues_list = load_venues(data_file("venues.json"))
    programs_list = load_programs(
        data_file("programs.json"),
        artists_list,
        venues_list,
    )
    program = find_program_by_id(programs_list, program_id)

    if program is None:
        content = f"""
        <h1 class="text-danger">Программа не найдена</h1>
        <a href="{reverse('programs')}" class="btn btn-outline-secondary">
            ← к списку программ
        </a>
        """
        return HttpResponse(
            page("Программа не найдена", content),
            status=404,
        )

    tickets_list = load_tickets(data_file("tickets.json"), programs_list)
    sold = count_active_tickets_by_program(tickets_list, program.id)
    status = "предстоит" if program.is_upcoming() else "прошла"
    badge = "bg-success" if program.is_upcoming() else "bg-secondary"
    artist_url = reverse("artist_detail", args=[program.artist.id])
    venue_url = reverse("venue_detail", args=[program.venue.id])

    content = f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">{escape(program.title)}</h5>
            <p class="card-text">
                <strong>ID:</strong> {program.id}
            </p>
            <p class="card-text">
                <strong>Исполнитель:</strong>
                <a href="{artist_url}">{escape(program.artist.name)}</a>
            </p>
            <p class="card-text">
                <strong>Площадка:</strong>
                <a href="{venue_url}">{escape(program.venue.name)}</a>
            </p>
            <p class="card-text">
                <strong>Жанр:</strong> {escape(program.genre)}
            </p>
            <p class="card-text">
                <strong>Дата:</strong> {program.event_date}
                <span class="badge {badge}">{status}</span>
            </p>
            <p class="card-text">
                <strong>Базовая цена:</strong>
                {program.base_price:.2f} руб.
            </p>
            <p class="card-text">
                <strong>Активных билетов:</strong> {sold}
            </p>
            <a href="{reverse('programs')}"
               class="btn btn-outline-secondary">
                ← к списку программ
            </a>
        </div>
    </div>
    """
    return HttpResponse(page(program.title, content), status=200)
