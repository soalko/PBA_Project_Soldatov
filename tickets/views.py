from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import escape

from homepage.views import data_file, page
from models.tickets import find_ticket_by_id
from storage import (
    load_artists,
    load_programs,
    load_tickets,
    load_venues,
)


def tickets(request):
    """Страница списка билетов."""
    artists_list = load_artists(data_file("artists.json"))
    venues_list = load_venues(data_file("venues.json"))
    programs_list = load_programs(
        data_file("programs.json"),
        artists_list,
        venues_list,
    )
    tickets_list = load_tickets(data_file("tickets.json"), programs_list)

    items = ""
    for ticket in tickets_list:
        url = reverse("ticket_detail", args=[ticket.id])
        status = "активен" if ticket.is_active() else "отменён"
        badge = "bg-success" if ticket.is_active() else "bg-secondary"
        items += f"""
        <li class="list-group-item d-flex justify-content-between
                   align-items-center gap-2">
            <a href="{url}">
                Билет №{ticket.id} – {escape(ticket.program.title)},
                место {escape(ticket.seat)}
            </a>
            <span class="badge {badge}">{status}</span>
        </li>
        """
    if not items:
        items = '<li class="list-group-item">Проданных билетов нет</li>'
    content = f"""
    <h1>Билеты</h1>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page("Билеты", content))


def ticket_detail(request, ticket_id):
    """Страница билета; для неизвестного id - ответ с кодом 404."""
    artists_list = load_artists(data_file("artists.json"))
    venues_list = load_venues(data_file("venues.json"))
    programs_list = load_programs(
        data_file("programs.json"),
        artists_list,
        venues_list,
    )
    tickets_list = load_tickets(data_file("tickets.json"), programs_list)
    ticket = find_ticket_by_id(tickets_list, ticket_id)

    if ticket is None:
        content = f"""
        <h1 class="text-danger">Билет не найден</h1>
        <a href="{reverse('tickets')}" class="btn btn-outline-secondary">
            ← к списку билетов
        </a>
        """
        return HttpResponse(
            page("Билет не найден", content),
            status=404,
        )

    status = "активен" if ticket.is_active() else "отменён"
    badge = "bg-success" if ticket.is_active() else "bg-secondary"
    program = ticket.program
    program_url = reverse("program_detail", args=[program.id])

    content = f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">Билет №{ticket.id}</h5>
            <p class="card-text">
                <strong>Программа:</strong>
                <a href="{program_url}">{escape(program.title)}</a>
            </p>
            <p class="card-text">
                <strong>Исполнитель:</strong> {escape(program.artist.name)}
            </p>
            <p class="card-text">
                <strong>Площадка:</strong> {escape(program.venue.name)}
            </p>
            <p class="card-text">
                <strong>Дата:</strong> {program.event_date}
            </p>
            <p class="card-text">
                <strong>Место:</strong> {escape(ticket.seat)}
                ({escape(ticket.category)})
            </p>
            <p class="card-text">
                <strong>Цена:</strong> {ticket.price:.2f} руб.
            </p>
            <p class="card-text">
                <strong>Статус:</strong>
                <span class="badge {badge}">{status}</span>
            </p>
            <a href="{reverse('tickets')}"
               class="btn btn-outline-secondary">
                ← к списку билетов
            </a>
        </div>
    </div>
    """
    return HttpResponse(page(f"Билет №{ticket.id}", content), status=200)
