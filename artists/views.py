from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import escape

from homepage.views import data_file, page
from models.artists import find_artist_by_id
from storage import load_artists


def artists(request):
    """Страница списка исполнителей."""
    items = ""
    for artist in load_artists(data_file("artists.json")):
        url = reverse("artist_detail", args=[artist.id])
        items += f"""
        <li class="list-group-item d-flex justify-content-between
                   align-items-center gap-2">
            <a href="{url}">{escape(artist.name)}</a>
            <span class="badge bg-info">{escape(artist.genre)}</span>
        </li>
        """
    if not items:
        items = '<li class="list-group-item">Список исполнителей пуст</li>'
    content = f"""
    <h1>Исполнители</h1>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page("Исполнители", content))


def artist_detail(request, artist_id):
    """Страница исполнителя; для неизвестного id - ответ с кодом 404."""
    artists_list = load_artists(data_file("artists.json"))
    artist = find_artist_by_id(artists_list, artist_id)

    if artist is None:
        content = f"""
        <h1 class="text-danger">Исполнитель не найден</h1>
        <a href="{reverse('artists')}" class="btn btn-outline-secondary">
            ← к списку исполнителей
        </a>
        """
        return HttpResponse(
            page("Исполнитель не найден", content),
            status=404,
        )

    content = f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">{escape(artist.name)}</h5>
            <p class="card-text">
                <strong>ID:</strong> {artist.id}
            </p>
            <p class="card-text">
                <strong>Страна:</strong> {escape(artist.country)}
            </p>
            <p class="card-text">
                <strong>Жанр:</strong>
                <span class="badge bg-info">{escape(artist.genre)}</span>
            </p>
            <a href="{reverse('artists')}"
               class="btn btn-outline-secondary">
                ← к списку исполнителей
            </a>
        </div>
    </div>
    """
    return HttpResponse(page(artist.name, content), status=200)
