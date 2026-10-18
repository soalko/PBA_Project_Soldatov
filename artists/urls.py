from django.urls import path

from . import views

app_name = "artists"

urlpatterns = [
    path("", views.artists, name="list"),
    path("<int:artist_id>/", views.artist_detail, name="detail"),
]
