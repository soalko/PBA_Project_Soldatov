from django.shortcuts import render


def index(request):
    """Главная страница: описание приложения и переходы к разделам."""
    return render(request, "homepage/index.html")


def page_not_found(request, exception):
    """Обработчик ошибки 404: адресу не соответствует ни один маршрут."""
    return render(request, "homepage/404.html", status=404)
