# Система управления концертными программами

Приложение для ведения реестра концертных программ, исполнителей
и площадок, а также продажи билетов. Консольная версия (ПР1–ПР3)
дополнена веб-интерфейсом на Django (ПР5), который в ПР6 переведён
на систему шаблонов Django (Django Template Language).

## Назначение

Приложение решает задачу упорядочивания работы концертного агента
или организатора мероприятий: ведёт реестр программ и исполнителей,
учитывает площадки и расписание, позволяет продавать и отменять
билеты с расчётом цены по промокоду. Данные сохраняются в JSON-файлах.

Приложение позволяет:

- просматривать в браузере исполнителей, площадки, программы и билеты;
- просматривать страницу отдельного объекта каждой сущности;
- видеть доступность площадки на текущую дату;
- видеть статус программы и число активных билетов на неё;
- в консольной версии — добавлять исполнителей, площадки и программы,
  искать программы, продавать и отменять билеты.

## Используемые технологии

- Python 3.11;
- Django 5.2 — веб-фреймворк;
- Django Template Language (DTL) — шаблоны страниц;
- HTML5 — разметка веб-страниц;
- CSS3 и Bootstrap 5.3 — оформление страниц;
- JavaScript — небольшое клиентское поведение;
- JSON — хранение данных;
- pytest — автоматизированные тесты;
- flake8 — проверка качества кода.

## Целевая аудитория

Концертные агенты, администраторы площадок и менеджеры по продаже
билетов.

## Предметная область

Организация и проведение концертных мероприятий. Программа связывает
исполнителя и площадку на конкретную дату; билеты продаются на
программу и содержат информацию о месте, категории и цене.

## Основные сущности (объектная модель)

### Artist — исполнитель
Атрибуты: `id`, `name`, `country`, `genre`.
Методы: `__init__`, `__str__`, `from_data`, `to_data`.

### Venue — площадка
Атрибуты: `id`, `name`, `address`, `capacity`.
Методы: `__init__`, `__str__`, `is_suitable_for`, `validate_capacity`
(`@staticmethod`), `from_data`, `to_data`.

### Program — концертная программа
Атрибуты: `id`, `title`, `artist` (объект `Artist`),
`venue` (объект `Venue`), `genre`, `event_date`, `base_price`.
Методы: `__init__`, `__str__`, `is_upcoming`,
`validate` (`@staticmethod`), `from_data`, `to_data`.

### Ticket — билет
Атрибуты: `id`, `program` (объект `Program`), `seat`,
`category`, `price`, `status`.
Методы: `__init__`, `__str__`, `is_active`, `cancel`,
`from_data`, `to_data`.

## Взаимодействие объектов

- `Program.artist → Artist` — композиция;
- `Program.venue → Venue` — композиция;
- `Ticket.program → Program` — композиция.

Благодаря ссылкам доступ к связанным данным выполняется напрямую:
`ticket.program.artist.name`, `ticket.program.venue.address`.
Эти же связи используются на веб-страницах программы и билета.

## Страницы веб-интерфейса

| URL | Имя маршрута | Шаблон | Страница |
|-----|--------------|--------|----------|
| `/` | `homepage:index` | `homepage/index.html` | главная: описание приложения и навигация |
| `/artists/` | `artists:list` | `artists/artist_list.html` | список исполнителей |
| `/artists/<int:artist_id>/` | `artists:detail` | `artists/artist_detail.html` | карточка исполнителя |
| `/venues/` | `venues:list` | `venues/venue_list.html` | список площадок |
| `/venues/<int:venue_id>/` | `venues:detail` | `venues/venue_detail.html` | карточка площадки, доступность на текущую дату |
| `/programs/` | `programs:list` | `programs/program_list.html` | список программ по дате |
| `/programs/<int:program_id>/` | `programs:detail` | `programs/program_detail.html` | карточка программы, исполнитель, площадка, активные билеты |
| `/tickets/` | `tickets:list` | `tickets/ticket_list.html` | список билетов со статусами |
| `/tickets/<int:ticket_id>/` | `tickets:detail` | `tickets/ticket_detail.html` | карточка билета и связанной программы |

Если объект с указанным идентификатором не найден, страница
возвращает ответ с кодом статуса 404: view передаёт в шаблон
`None`, шаблон через `{% if %}` / `{% else %}` выводит сообщение
(«Площадка не найдена» и т. п.), а `render(..., status=404)` задаёт
код ответа. Адреса, которым не соответствует ни один маршрут,
обрабатывает общий обработчик `handler404`
(`homepage.views.page_not_found`, шаблон `homepage/404.html`);
он виден при `DEBUG = False`.

## Маршрутизация

Маршруты разделены на два уровня:

- `concerts/urls.py` — корневой файл: функцией `include()` подключает
  маршруты приложений по префиксам `artists/`, `venues/`, `programs/`,
  `tickets/` и объявляет `handler404`;
- `<приложение>/urls.py` — адреса внутри раздела: список и страница
  объекта с конвертером пути `<int:...>`.

В каждом `urls.py` приложения задано пространство имён
(`app_name = "venues"` и т. д.), у каждого маршрута есть имя
(`name="list"`, `name="detail"`). Полное имя маршрута складывается
из пространства имён и имени: `venues:list`, `venues:detail`.
Ссылки в шаблонах формируются тегом `{% url %}`, а не жёстко
заданными адресами:

```text
{% url 'venues:list' %}
{% url 'venues:detail' venue.id %}
{% url 'tickets:detail' ticket.id %}
```

## Шаблоны Django (ПР6)

HTML больше не формируется в Python-коде: функция `page()` из ПР5
удалена. View-функция загружает данные, кладёт их в словарь
контекста и вызывает `render()`:

```text
HTTP-запрос → URLconf → view → context → шаблон → HTML → HTTP-ответ
```

```python
def venues(request):
    venues_list = load_venues(data_file("venues.json"))
    context = {"venues": venues_list}
    return render(request, "venues/venue_list.html", context)
```

### Расположение шаблонов

- `templates/` — каталог уровня проекта, подключён в
  `settings.TEMPLATES["DIRS"]`: `base.html` и
  `includes/navigation.html`;
- `<приложение>/templates/<приложение>/` — шаблоны приложения,
  находятся благодаря `APP_DIRS = True`. Вложенный каталог с именем
  приложения исключает конфликт одноимённых шаблонов.

### Базовый шаблон и наследование

`templates/base.html` содержит общую HTML-структуру: `DOCTYPE`,
`<head>`, Bootstrap, собственный CSS, навигацию, контейнер, подвал и
JavaScript. В нём объявлены блоки:

```text
{% block title %}Концертные программы{% endblock %}
{% block content %}{% endblock %}
```

Все страницы начинаются с `{% extends "base.html" %}` и
переопределяют эти блоки.

### Включаемые шаблоны (`{% include %}`)

| Фрагмент | Где подключается |
|----------|------------------|
| `templates/includes/navigation.html` | `base.html` |
| `artists/includes/artist_card.html` | список исполнителей |
| `venues/includes/venue_card.html` | список площадок |
| `programs/includes/program_status.html` | список и страница программы |
| `tickets/includes/ticket_status.html` | список и страница билета |

Включаемый шаблон получает текущий контекст: внутри цикла
`{% for venue in venues %}` фрагмент `venue_card.html` видит
переменную `venue`.

### Циклы и условия

- `{% for ... %} ... {% empty %} ... {% endfor %}` — списки всех
  сущностей; `{% empty %}` выводит «Список ... пуст»;
- `{% if program.is_upcoming %}` — «предстоит» / «прошла»;
- `{% if ticket.is_active %}` — «активен» / «отменён»;
- `{% if is_available %}` — площадка «свободна» / «занята»;
- `{% if venue %}` — объект найден или нет (страница 404).

Бизнес-логика остаётся в Python: доступность площадки вычисляет
`is_venue_available()` во view, число активных билетов —
`count_active_tickets_by_program()`; шаблон только выводит результат.

### Фильтры шаблонов

| Фильтр | Пример | Назначение |
|--------|--------|------------|
| `length` | `{{ venues\|length }}` | количество элементов списка |
| `default` | `{{ venue.name\|default:"Без названия" }}` | значение для пустого поля |
| `date` | `{{ program.event_day\|date:"d.m.Y" }}` | формат даты `20.11.2026` |
| `floatformat` | `{{ ticket.price\|floatformat:2 }}` | цена с двумя знаками |
| `capfirst` | `{{ artist.genre\|capfirst }}` | жанр с заглавной буквы |
| `upper` | `{{ ticket.seat\|upper }}` | номер места в верхнем регистре |

Для фильтра `date` у класса `Program` добавлено свойство
`event_day` — дата как объект `date`; в JSON по-прежнему хранится
строка `event_date`. Значения автоматически экранируются шаблонизатором
(функция `escape()` из ПР5 больше не нужна).

## Статические файлы

Собственные статические файлы лежат в `homepage/static/homepage/`:

| Файл | Где используется |
|------|------------------|
| `css/style.css` | `base.html`; классы `site-header`, `site-logo`, `entity-card`, `status-badge`, `ticket-status-cancelled`, `empty-message` |
| `js/main.js` | `base.html`: текущий год в подвале и подсветка раздела в меню |
| `img/logo.png` | `navigation.html`: логотип в шапке |

Подключение в шаблоне:

```text
{% load static %}
<link rel="stylesheet" href="{% static 'homepage/css/style.css' %}">
<img src="{% static 'homepage/img/logo.png' %}" alt="...">
<script src="{% static 'homepage/js/main.js' %}"></script>
```

Bootstrap 5.3 (CDN) сохранён для базовой вёрстки; собственный CSS
дополняет его стилями проекта. Проверка поиска файла:
`python manage.py findstatic homepage/img/logo.png`.

## Основные операции

### Используются в веб-интерфейсе (ПР5–ПР6)

- загрузка данных: `load_artists()`, `load_venues()`,
  `load_programs()`, `load_tickets()`;
- поиск по идентификатору: `find_artist_by_id()`, `find_venue_by_id()`,
  `find_program_by_id()`, `find_ticket_by_id()`;
- проверка доступности площадки на дату: `is_venue_available()`;
- сортировка программ по дате: `sort_programs_by_date()`;
- подсчёт активных билетов: `count_active_tickets_by_program()`;
- методы объектов: `Program.is_upcoming()`, `Ticket.is_active()`.

### Отложены до следующих работ

Операции работают в консольной версии; в веб-интерфейсе появятся
вместе с формами и POST-запросами:

- добавление исполнителя, площадки, программы;
- поиск по названию и фильтрация по жанру и вместимости;
- продажа билета с расчётом цены по промокоду;
- отмена билета, удаление программы.

## Хранение данных

Данные хранятся в JSON-файлах каталога `data/`:
`artists.json`, `venues.json`, `programs.json`, `tickets.json`.

При загрузке: `JSON → dict → объект` с восстановлением связей
через идентификаторы. При сохранении: `объект → dict → JSON`.
Веб-версия читает те же файлы; путь к каталогу задан настройкой
`DATA_DIR` в `concerts/settings.py`. Django ORM пока не используется,
база данных Django (`db.sqlite3`) нужна только служебным приложениям
фреймворка. Формы ещё не реализованы; переход на базу данных
относится к следующим практическим работам.

## Структура проекта

```text
PBA_Project_Soldatov/
├── README.md
├── requirements.txt
├── manage.py              # команды управления Django-проектом
├── main.py                # консольная версия (ПР3)
├── storage.py             # загрузка и сохранение JSON
├── utils.py               # функции консольного ввода
│
├── concerts/              # конфигурация Django-проекта
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── templates/             # шаблоны уровня проекта
│   ├── base.html
│   └── includes/
│       └── navigation.html
│
├── homepage/              # приложение: главная страница, 404, статика
│   ├── static/homepage/
│   │   ├── css/style.css
│   │   ├── js/main.js
│   │   └── img/logo.png
│   ├── templates/homepage/
│   │   ├── index.html
│   │   └── 404.html
│   ├── urls.py
│   └── views.py
│
├── artists/               # приложение: исполнители
│   └── templates/artists/
│       ├── artist_list.html
│       ├── artist_detail.html
│       └── includes/artist_card.html
├── venues/                # приложение: площадки
│   └── templates/venues/
│       ├── venue_list.html
│       ├── venue_detail.html
│       └── includes/venue_card.html
├── programs/              # приложение: концертные программы
│   └── templates/programs/
│       ├── program_list.html
│       ├── program_detail.html
│       └── includes/program_status.html
├── tickets/               # приложение: билеты
│   ├── templates/tickets/
│   │   ├── ticket_list.html
│   │   ├── ticket_detail.html
│   │   └── includes/ticket_status.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── models/                # классы предметной области (ПР3)
│   ├── __init__.py
│   ├── artists.py
│   ├── venues.py
│   ├── programs.py
│   └── tickets.py
│
├── data/                  # JSON-файлы данных
└── tests/                 # автоматизированные тесты pytest
    ├── conftest.py
    ├── test_artists.py
    ├── test_venues.py
    ├── test_programs.py
    ├── test_tickets.py
    └── test_web.py
```

Все пять приложений имеют одинаковый набор Python-файлов (показан
на примере `tickets/`).

## Назначение модулей

### `concerts/`

Пакет настроек Django-проекта:

- `settings.py` — настройки: `INSTALLED_APPS`, `DEBUG`,
  `ALLOWED_HOSTS`, локализация, `DATA_DIR`, каталог шаблонов
  `TEMPLATES["DIRS"]`;
- `urls.py` — маршрутизация верхнего уровня и `handler404`;
- `asgi.py`, `wsgi.py` — точки взаимодействия с сервером.

### `homepage/`

Приложение главной страницы — точки входа в проект:

- `views.py` — `data_file()` (путь к JSON-файлу), view-функции
  `index()` и `page_not_found()`;
- `urls.py` — маршрут главной страницы (`homepage:index`);
- `templates/homepage/` — главная страница и страница 404;
- `static/homepage/` — собственные CSS, JavaScript и логотип.

Остальные приложения импортируют `data_file()` отсюда.

### `artists/`, `venues/`, `programs/`, `tickets/`

Приложения разделов. В каждом:

- `views.py` — view-функция списка и view-функция страницы объекта:
  загружают данные, готовят контекст и вызывают `render()`;
- `urls.py` — пространство имён `app_name` и маршруты `list`, `detail`;
- `templates/<приложение>/` — шаблоны списка, страницы объекта и
  включаемый фрагмент `includes/`;
- `models.py` — Django-модели (появятся в следующих работах).

Отдельное приложение для пользователей не создаётся: в проекте нет
такой сущности, а для учётных записей Django предоставляет
встроенное приложение `django.contrib.auth`.

### `models/`

Классы предметной области и функции работы с коллекциями (ПР3):
`Artist`, `Venue`, `Program`, `Ticket`. Не путать с файлами
`models.py` Django-приложений.

### `storage.py`, `utils.py`, `main.py`

Хранилище JSON, функции безопасного консольного ввода и консольное
меню. Сохранены с ПР3 и продолжают работать.

## Установка зависимостей

```text
pip install -r requirements.txt
```

Состав `requirements.txt`: `Django==5.2.*`, `pytest`, `flake8`.

## Запуск приложения

Веб-версия (Django):

```text
python manage.py migrate
python manage.py check
python manage.py runserver
```

После запуска открыть в браузере адрес `http://127.0.0.1:8000/`.

Консольная версия (сохранена):

```text
python main.py
```

## Запуск тестов

```text
pytest -v
```

Тесты `tests/test_web.py` обращаются к страницам через тестовый
HTTP-клиент Django и используют собственный набор JSON-данных.
Они проверяют, какие шаблоны использованы (`response.templates`),
наследование от `base.html`, подключение фрагментов `include`,
содержимое контекста, именованные URL, фильтры, обработку пустого
списка, подключение статических файлов и коды ответа 404.

## Проверка качества кода

```text
flake8 . --extend-exclude=venv
```

## Текущее состояние и план развития

Реализовано (ПР5):

- Django-проект `concerts` и пять приложений: `homepage`, `artists`,
  `venues`, `programs`, `tickets`;
- маршрутизация URL двух уровней с динамическими адресами;
- view-функции и девять веб-страниц;
- отображение данных предметной области из JSON-файлов;
- проверка доступности площадки и статусы через логику ПР3;
- навигация между страницами, собственная страница ошибки 404;
- оформление Bootstrap 5.3 и собственные CSS-правила.

Реализовано (ПР6):

- перевод всех страниц на шаблоны Django и функцию `render()`;
- базовый шаблон `base.html`, наследование `extends`, блоки `block`;
- навигация и повторяющиеся фрагменты вынесены в `include`;
- передача данных через контекст, циклы `for`/`empty`, условия `if`;
- пространства имён URL и ссылки через `{% url %}`;
- фильтры `length`, `default`, `date`, `floatformat`, `capfirst`, `upper`;
- статические файлы: собственные CSS, JavaScript и логотип;
- функция `page()` удалена.

Планируется:

- перенос сущностей `Artist`, `Venue`, `Program`, `Ticket` в Django ORM;
- подключение базы данных;
- формы создания программ и продажи билетов;
- использование отложенной логики ПР3 в веб-интерфейсе.

## Преемственность с ПР1–ПР3

- `Program.validate()` — развитие сценария ПР1
  (`check_program_creation`);
- `get_booking_status()` — без изменений перенесена из ПР1;
- `calculate_ticket_price()` — развитие сценария ПР1;
- функциональная модель ПР2 переработана в объектную (ПР3):
  словари заменены классами, коллекции — списками объектов;
- в ПР5 код ПР3 не удалён: view-функции вызывают те же функции
  загрузки, поиска и проверки, что и консольные сценарии `main.py`;
- в ПР6 изменился только слой представления: источник данных
  (JSON и классы ПР3) остался прежним.
