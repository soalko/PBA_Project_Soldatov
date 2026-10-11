from django.urls import path

from . import views

urlpatterns = [
    path("", views.artists, name="artists"),
    path("<int:artist_id>/", views.artist_detail, name="artist_detail"),
]
