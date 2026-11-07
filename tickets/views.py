from decimal import Decimal

from django.core.paginator import Paginator
from django.db.models import (
    Avg,
    Count,
    DecimalField,
    F,
    Max,
    Min,
    Q,
    Sum,
    Value,
)
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, render

from programs.models import Program
from venues.models import Venue

from .models import Ticket

# Билетов на одной странице списка.
PAGE_SIZE = 5

# Разрешённые значения ?sort= для списка билетов.
SORT_FIELDS = {
    "id": ("pk",),
    # Сортировка по полю связанной модели Program.
    "date": ("program__event_date", "pk"),
    "program": ("program__title", "seat"),
    "price": ("price", "pk"),
    "-price": ("-price", "pk"),
}
DEFAULT_SORT = "id"

DEFAULT_MIN_SOLD = 2

# Условие «билет продан» со стороны программы: используется внутри
# агрегатных функций, чтобы не учитывать отменённые билеты.
SOLD_TICKETS = Q(tickets__status=Ticket.Status.SOLD)


def tickets(request):
    """Список билетов: фильтры, сортировка и постраничный вывод.

    Пример адреса: /tickets/?venue=1&status=sold&sort=-price&page=2
    Параметры проверяются: нечисловой id и неизвестный статус
    игнорируются, неизвестная сортировка заменяется на «по номеру».
    """
    program_id = request.GET.get("program", "").strip()
    venue_id = request.GET.get("venue", "").strip()
    status = request.GET.get("status", "").strip()
    sort = request.GET.get("sort", DEFAULT_SORT)
    if sort not in SORT_FIELDS:
        sort = DEFAULT_SORT

    # Программа и её площадка подгружаются одним запросом с JOIN.
    tickets_list = Ticket.objects.select_related(
        "program",
        "program__venue",
    )

    # Каждый filter() добавляет условие через AND и сужает выборку.
    if program_id.isdigit():
        # Фильтр по внешнему ключу program_id.
        tickets_list = tickets_list.filter(program_id=int(program_id))
    if venue_id.isdigit():
        # Фильтр по полю связанной модели: площадка программы.
        tickets_list = tickets_list.filter(
            program__venue_id=int(venue_id),
        )
    if status in Ticket.Status.values:
        tickets_list = tickets_list.filter(status=status)

    tickets_list = tickets_list.order_by(*SORT_FIELDS[sort])

    # Пагинация после фильтров и сортировки. get_page() не падает
    # на ?page=abc или ?page=999: вернёт первую или последнюю
    # страницу. В SQL это LIMIT/OFFSET.
    paginator = Paginator(tickets_list, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "tickets": page_obj,
        "page_obj": page_obj,
        "programs": Program.objects.order_by("event_date", "title"),
        "venues": Venue.objects.order_by("name"),
        "status_choices": Ticket.Status.choices,
        "selected_program": program_id,
        "selected_venue": venue_id,
        "selected_status": status,
        "sort": sort,
    }
    return render(request, "tickets/ticket_list.html", context)


def ticket_detail(request, ticket_id):
    """Страница билета; неизвестный id — ответ 404.

    Двойное подчёркивание в select_related проходит по цепочке
    связей: билет -> программа -> исполнитель и площадка.
    """
    ticket = get_object_or_404(
        Ticket.objects.select_related(
            "program__artist",
            "program__venue",
        ),
        pk=ticket_id,
    )
    return render(request, "tickets/ticket_detail.html", {"ticket": ticket})


def parse_min_sold(value):
    """Порог «популярной» программы из ?min_sold=N и текст ошибки."""
    if not value:
        return DEFAULT_MIN_SOLD, None
    try:
        min_sold = int(value)
    except ValueError:
        return DEFAULT_MIN_SOLD, "Порог должен быть целым числом."
    if min_sold < 1:
        return DEFAULT_MIN_SOLD, "Порог должен быть не меньше 1."
    return min_sold, None


def statistics(request):
    """Статистика продаж: aggregate(), annotate() и группировка."""
    min_sold, error = parse_min_sold(
        request.GET.get("min_sold", "").strip(),
    )

    # aggregate() считает итог по всему набору и возвращает словарь.
    # Отменённые билеты исключены фильтром до подсчёта.
    sales = Ticket.objects.filter(status=Ticket.Status.SOLD).aggregate(
        tickets_sold=Count("pk"),
        revenue=Sum("price"),
        average_price=Avg("price"),
    )
    prices = Program.objects.aggregate(
        programs_count=Count("pk"),
        min_price=Min("base_price"),
        max_price=Max("base_price"),
    )

    # annotate() считает показатели для каждой программы отдельно.
    # Запрос начинается с Program, поэтому программы без продаж
    # тоже попадают в результат (аналог LEFT JOIN); условие
    # filter=SOLD_TICKETS действует только внутри Count и Sum.
    by_program = (
        Program.objects.annotate(
            tickets_sold=Count("tickets", filter=SOLD_TICKETS),
            # Coalesce заменяет NULL (нет продаж) на 0.
            revenue=Coalesce(
                Sum("tickets__price", filter=SOLD_TICKETS),
                Value(Decimal("0")),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
            # F() берёт значение поля связанной модели.
            venue_name=F("venue__name"),
        )
        .values("title", "venue_name", "tickets_sold", "revenue")
        .order_by("-tickets_sold", "title")
    )

    by_venue = Venue.objects.annotate(
        programs_count=Count("programs"),
    ).order_by("-programs_count", "name")

    # values("genre") перед annotate() — группировка по жанру
    # (GROUP BY genre): одна строка результата на каждый жанр.
    by_genre = (
        Program.objects.values("genre")
        .annotate(
            programs_count=Count("pk"),
            average_price=Avg("base_price"),
        )
        .order_by("-programs_count", "genre")
    )

    # Условие на вычисляемое поле превращается в HAVING.
    popular = by_program.filter(tickets_sold__gte=min_sold)

    context = {
        "sales": sales,
        "prices": prices,
        "by_program": by_program,
        "by_venue": by_venue,
        "by_genre": by_genre,
        "popular": popular,
        "min_sold": min_sold,
        "error": error,
    }
    return render(request, "tickets/statistics.html", context)
