from django.conf import settings
from django.shortcuts import render


def data_file(name):
    """Вернуть путь к JSON-файлу проекта ПР3 из каталога data/."""
    return str(settings.DATA_DIR / name)


def index(request):
    """Главная страница: описание приложения и переходы к разделам."""
    return render(request, "homepage/index.html")


def page_not_found(request, exception):
    """Обработчик ошибки 404: адресу не соответствует ни один маршрут."""
    return render(request, "homepage/404.html", status=404)
