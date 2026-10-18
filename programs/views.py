from django.shortcuts import render

from homepage.views import data_file
from models.programs import find_program_by_id, sort_programs_by_date
from models.tickets import count_active_tickets_by_program
from storage import (
    load_artists,
    load_programs,
    load_tickets,
    load_venues,
)


def load_all_programs():
    """Загрузить программы со связанными исполнителями и площадками."""
    artists_list = load_artists(data_file("artists.json"))
    venues_list = load_venues(data_file("venues.json"))
    return load_programs(
        data_file("programs.json"),
        artists_list,
        venues_list,
    )


def programs(request):
    """Страница списка концертных программ, упорядоченных по дате."""
    programs_list = sort_programs_by_date(load_all_programs())

    context = {
        "programs": programs_list,
    }

    return render(request, "programs/program_list.html", context)


def program_detail(request, program_id):
    """Страница программы; для неизвестного id - ответ с кодом 404."""
    programs_list = load_all_programs()
    program = find_program_by_id(programs_list, program_id)

    sold = 0
    if program is not None:
        tickets_list = load_tickets(
            data_file("tickets.json"),
            programs_list,
        )
        sold = count_active_tickets_by_program(tickets_list, program.id)

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
