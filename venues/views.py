from datetime import date

from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from programs.models import Program

from .models import Venue


def venues(request):
    """Список площадок: сначала самые вместительные."""
    # Второе поле сортировки упорядочивает площадки
    # с одинаковой вместимостью.
    venues_list = Venue.objects.order_by("-capacity", "name")

    context = {
        "venues": venues_list,
    }
    return render(request, "venues/venue_list.html", context)


def venue_detail(request, venue_id):
    """Страница площадки с её программами; неизвестный id — 404."""
    venue = get_object_or_404(Venue, pk=venue_id)
    today = timezone.localdate()

    # Обратная связь venue.programs: программы этой площадки
    # вместе с исполнителями (select_related — JOIN в одном запросе).
    programs_list = venue.programs.select_related("artist").order_by(
        "event_date",
    )

    context = {
        "venue": venue,
        "programs": programs_list,
        "is_available": venue.is_free_on(today),
        "today": today,
    }
    return render(request, "venues/venue_detail.html", context)


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
        # id площадок, на которых в эту дату уже есть программа.
        # values_list(..., flat=True) возвращает только числа,
        # а не объекты программ.
        busy_venue_ids = Program.objects.filter(
            event_date=event_date,
        ).values_list("venue_id", flat=True)

        # Фильтр по вместимости и исключение занятых площадок.
        # Подзапрос busy_venue_ids попадает в SQL как NOT IN (...).
        venues_list = (
            Venue.objects.filter(capacity__gte=capacity)
            .exclude(pk__in=busy_venue_ids)
            .order_by("capacity", "name")
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
