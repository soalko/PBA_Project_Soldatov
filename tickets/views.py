from django.shortcuts import render

from homepage.views import data_file
from models.tickets import find_ticket_by_id
from programs.views import load_all_programs
from storage import load_tickets


def load_all_tickets():
    """Загрузить билеты со связанными программами."""
    return load_tickets(data_file("tickets.json"), load_all_programs())


def tickets(request):
    """Страница списка билетов."""
    context = {
        "tickets": load_all_tickets(),
    }

    return render(request, "tickets/ticket_list.html", context)


def ticket_detail(request, ticket_id):
    """Страница билета; для неизвестного id - ответ с кодом 404."""
    ticket = find_ticket_by_id(load_all_tickets(), ticket_id)

    context = {
        "ticket": ticket,
    }

    return render(
        request,
        "tickets/ticket_detail.html",
        context,
        status=404 if ticket is None else 200,
    )
