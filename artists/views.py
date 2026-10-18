from django.shortcuts import render

from homepage.views import data_file
from models.artists import find_artist_by_id
from storage import load_artists


def artists(request):
    """Страница списка исполнителей."""
    artists_list = load_artists(data_file("artists.json"))

    context = {
        "artists": artists_list,
    }

    return render(request, "artists/artist_list.html", context)


def artist_detail(request, artist_id):
    """Страница исполнителя; для неизвестного id - ответ с кодом 404."""
    artists_list = load_artists(data_file("artists.json"))
    artist = find_artist_by_id(artists_list, artist_id)

    context = {
        "artist": artist,
    }

    return render(
        request,
        "artists/artist_detail.html",
        context,
        status=404 if artist is None else 200,
    )
