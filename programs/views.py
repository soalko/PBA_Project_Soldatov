from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from tickets.models import Ticket

from .models import Program

# Разрешённые значения параметра ?sort= и поля сортировки.
# Пользовательский ввод не передаётся в order_by() напрямую:
# неизвестное значение заменяется сортировкой по дате.
SORT_FIELDS = {
    "date": ("event_date", "title"),
    "title": ("title", "event_date"),
    "price": ("base_price", "event_date"),
    "-price": ("-base_price", "event_date"),
    # Сортировка по полю связанной модели Artist.
    "artist": ("artist__name", "event_date"),
}
DEFAULT_SORT = "date"


def programs(request):
    """Афиша: поиск, фильтр по жанру и выбор сортировки.

    Пример адреса: /programs/?q=джаз&genre=джаз&sort=-price
    """
    query = request.GET.get("q", "").strip()
    genre = request.GET.get("genre", "").strip()
    sort = request.GET.get("sort", DEFAULT_SORT)
    if sort not in SORT_FIELDS:
        sort = DEFAULT_SORT

    # select_related() загружает исполнителя и площадку тем же
    # SQL-запросом (JOIN), поэтому шаблон не делает лишних запросов
    # при обращении к program.artist.name и program.venue.name.
    programs_list = Program.objects.select_related("artist", "venue")

    if query:
        # Поиск сразу по трём полям: название программы, имя
        # исполнителя и название площадки. Q-объекты, соединённые |,
        # дают в SQL условие OR.
        text = query.lower()
        programs_list = programs_list.filter(
            Q(title__lower__contains=text)
            | Q(artist__name__lower__contains=text)
            | Q(venue__name__lower__contains=text)
        )
    if genre:
        programs_list = programs_list.filter(genre=genre)

    programs_list = programs_list.order_by(*SORT_FIELDS[sort])

    genres = (
        Program.objects.order_by("genre")
        .values_list("genre", flat=True)
        .distinct()
    )

    context = {
        "programs": programs_list,
        "genres": genres,
        "query": query,
        "selected_genre": genre,
        "sort": sort,
    }
    return render(request, "programs/program_list.html", context)


def program_detail(request, program_id):
    """Страница программы; неизвестный id — ответ 404."""
    program = get_object_or_404(
        Program.objects.select_related("artist", "venue"),
        pk=program_id,
    )
    # Количество активных билетов через обратную связь program.tickets.
    sold = program.tickets.filter(status=Ticket.Status.SOLD).count()

    context = {
        "program": program,
        "sold": sold,
    }
    return render(request, "programs/program_detail.html", context)
