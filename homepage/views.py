from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import escape

# Собственные CSS-правила проекта: дополняют оформление Bootstrap.
STYLE = """
        body { background-color: #f8f9fa; }
        h1 { margin-bottom: 1rem; }
        .site-header { background-color: #212529; }
        .site-header .nav-link { color: #ffffff; }
        .site-header .nav-link:hover { color: #ffc107; }
        footer { color: #6c757d; font-size: 0.875rem; }
    """


def data_file(name):
    """Вернуть путь к JSON-файлу проекта ПР3 из каталога data/."""
    return str(settings.DATA_DIR / name)


def page(title, content):
    """Собрать HTML-документ с единым каркасом всех страниц проекта.

    title - заголовок вкладки браузера, content - HTML-разметка
    основной части страницы, подготовленная view-функцией.
    """
    bootstrap = (
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3"
        "/dist/css/bootstrap.min.css"
    )
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{escape(title)}</title>
    <link rel="stylesheet" href="{bootstrap}">
    <style>{STYLE}</style>
</head>
<body>
    <header class="site-header mb-4">
        <nav class="nav container py-2">
            <a class="nav-link" href="{reverse('index')}">Главная</a>
            <a class="nav-link" href="{reverse('artists')}">Исполнители</a>
            <a class="nav-link" href="{reverse('venues')}">Площадки</a>
            <a class="nav-link" href="{reverse('programs')}">Программы</a>
            <a class="nav-link" href="{reverse('tickets')}">Билеты</a>
        </nav>
    </header>
    <main class="container">{content}</main>
    <footer class="container py-4">
        Система управления концертными программами
    </footer>
</body>
</html>"""


def index(request):
    """Главная страница: описание приложения и переходы к разделам."""
    content = f"""
    <h1 class="display-5">Концертные программы</h1>
    <p class="lead">
        Система управления концертными программами: реестр исполнителей,
        площадок, программ и проданных билетов.
    </p>
    <p>Основные разделы:</p>
    <a href="{reverse('artists')}" class="btn btn-primary me-2 mb-2">
        Исполнители
    </a>
    <a href="{reverse('venues')}" class="btn btn-primary me-2 mb-2">
        Площадки
    </a>
    <a href="{reverse('programs')}" class="btn btn-primary me-2 mb-2">
        Программы
    </a>
    <a href="{reverse('tickets')}" class="btn btn-secondary mb-2">
        Билеты
    </a>
    """
    return HttpResponse(page("Концертные программы", content))


def page_not_found(request, exception):
    """Обработчик ошибки 404: адресу не соответствует ни один маршрут."""
    content = f"""
    <h1 class="text-danger">404 – страница не найдена</h1>
    <p>Проверьте адрес или вернитесь на главную.</p>
    <a href="{reverse('index')}" class="btn btn-primary">На главную</a>
    """
    return HttpResponse(
        page("404 – страница не найдена", content),
        status=404,
    )
