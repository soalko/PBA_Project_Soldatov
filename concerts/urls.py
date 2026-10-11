"""Корневая маршрутизация проекта.

Здесь адрес делится на две части: префикс раздела обрабатывается
в этом файле, а остаток передаётся функцией include() в urls.py
соответствующего приложения.
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("artists/", include("artists.urls")),
    path("venues/", include("venues.urls")),
    path("programs/", include("programs.urls")),
    path("tickets/", include("tickets.urls")),
]

# Обработчик ошибки 404 объявляется один раз для всего проекта.
handler404 = "homepage.views.page_not_found"
