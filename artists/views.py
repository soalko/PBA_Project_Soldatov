from django.db.models import Count
from django.shortcuts import get_object_or_404, render

from .models import Artist


def artists(request):
    """Список исполнителей с поиском по названию и фильтром по жанру.

    Пример адреса: /artists/?q=ветер&genre=рок
    """
    query = request.GET.get("q", "").strip()
    genre = request.GET.get("genre", "").strip()

    # annotate() добавляет каждому исполнителю вычисляемое поле:
    # число его программ (LEFT JOIN + GROUP BY + COUNT в SQL).
    # Исполнители без программ остаются в списке со значением 0.
    artists_list = Artist.objects.annotate(
        programs_count=Count("programs"),
    ).order_by("name")

    if query:
        # Поиск подстроки без учёта регистра, в том числе для
        # кириллицы (LOWER переопределена в homepage/apps.py).
        artists_list = artists_list.filter(
            name__lower__contains=query.lower(),
        )
    if genre:
        # Фильтрация по одному условию: точное совпадение жанра.
        artists_list = artists_list.filter(genre=genre)

    # Жанры без повторов для выпадающего списка (SELECT DISTINCT).
    genres = (
        Artist.objects.order_by("genre")
        .values_list("genre", flat=True)
        .distinct()
    )

    context = {
        "artists": artists_list,
        "genres": genres,
        "query": query,
        "selected_genre": genre,
    }
    return render(request, "artists/artist_list.html", context)


def artist_detail(request, artist_id):
    """Страница исполнителя и его программ; неизвестный id — 404."""
    artist = get_object_or_404(Artist, pk=artist_id)
    # Обратная связь artist.programs (related_name в модели Program).
    # select_related("venue") загружает площадки тем же запросом.
    programs_list = artist.programs.select_related("venue").order_by(
        "event_date",
    )

    context = {
        "artist": artist,
        "programs": programs_list,
    }
    return render(request, "artists/artist_detail.html", context)
