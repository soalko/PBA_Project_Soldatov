# Система управления концертными программами

Приложение для ведения реестра концертных программ, исполнителей
и площадок, а также продажи билетов. Консольная версия (ПР1–ПР3)
дополнена веб-интерфейсом на Django (ПР5), который в ПР6 переведён
на систему шаблонов Django (Django Template Language). В ПР7 данные
перенесены из JSON-файлов в реляционную базу SQLite: веб-страницы
получают их SQL-запросами через модуль `sqlite3`. В ПР9 слой данных
переведён на Django ORM: сущности описаны моделями, структура базы
управляется миграциями, представления получают данные через
менеджеры моделей.

## Назначение

Приложение решает задачу упорядочивания работы концертного агента
или организатора мероприятий: ведёт реестр программ и исполнителей,
учитывает площадки и расписание, позволяет продавать и отменять
билеты с расчётом цены по промокоду. Веб-версия хранит данные в базе
Django `db.sqlite3` и работает с ними через Django ORM, консольная —
в JSON-файлах.

Приложение позволяет:

- просматривать в браузере исполнителей, площадки, программы и билеты;
- просматривать страницу отдельного объекта каждой сущности;
- видеть доступность площадки на текущую дату;
- подбирать площадку, свободную в выбранную дату и вмещающую
  нужное число зрителей;
- искать исполнителей по названию и фильтровать их по жанру;
- искать программы по названию, исполнителю и площадке, сортировать
  афишу по дате, названию, исполнителю и цене;
- фильтровать билеты по программе, площадке и статусу, сортировать
  их и просматривать постранично;
- видеть статус программы и число активных билетов на неё;
- смотреть статистику продаж: выручку, продажи по программам,
  загрузку площадок, жанры и популярные программы;
- в консольной версии — добавлять исполнителей, площадки и программы,
  искать программы, продавать и отменять билеты.

## Используемые технологии

- Python 3.11;
- Django 5.2 — веб-фреймворк;
- Django Template Language (DTL) — шаблоны страниц;
- HTML5 — разметка веб-страниц;
- CSS3 и Bootstrap 5.3 — оформление страниц;
- JavaScript — небольшое клиентское поведение;
- Django ORM — модели, связи, миграции и запросы к базе (ПР9);
- SQLite — СУБД; язык SQL и модуль `sqlite3` — слой данных ПР7;
- JSON — исходные данные и хранилище консольной версии;
- pytest и pytest-django — автоматизированные тесты;
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
| `/artists/` | `artists:list` | `artists/artist_list.html` | список исполнителей, поиск `?q=`, фильтр `?genre=` |
| `/artists/<int:artist_id>/` | `artists:detail` | `artists/artist_detail.html` | карточка исполнителя и его программы |
| `/venues/` | `venues:list` | `venues/venue_list.html` | список площадок |
| `/venues/available/` | `venues:available` | `venues/available.html` | подбор свободной площадки по дате и вместимости |
| `/venues/<int:venue_id>/` | `venues:detail` | `venues/venue_detail.html` | карточка площадки, доступность на текущую дату |
| `/programs/` | `programs:list` | `programs/program_list.html` | афиша: поиск `?q=`, фильтр `?genre=`, сортировка `?sort=` |
| `/programs/<int:program_id>/` | `programs:detail` | `programs/program_detail.html` | карточка программы, исполнитель, площадка, активные билеты |
| `/tickets/` | `tickets:list` | `tickets/ticket_list.html` | билеты: фильтры `?program=`, `?venue=`, `?status=`, сортировка `?sort=`, страницы `?page=` |
| `/tickets/<int:ticket_id>/` | `tickets:detail` | `tickets/ticket_detail.html` | карточка билета и связанной программы |
| `/tickets/statistics/` | `tickets:statistics` | `tickets/statistics.html` | статистика продаж, порог `?min_sold=` |

Если объект с указанным идентификатором не найден, страница
возвращает ответ с кодом статуса 404: представление получает объект
функцией `get_object_or_404()`, которая при отсутствии записи
вызывает исключение `Http404`. Его, как и адреса без маршрута,
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
    context = {"venues": fetch_all(VENUE_LIST_SQL)}
    return render(request, "venues/venue_list.html", context)
```

С ПР7 данные для контекста получает SQL-запрос (см. раздел
«База данных SQLite»); шаблоны ПР6 сохранены.

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

Значения для условий вычисляет SQL-запрос, шаблон только выводит
результат: `is_upcoming` и `is_active` — вычисляемые столбцы
результата, доступность площадки — `COUNT(*)` программ на дату,
число активных билетов — `COUNT(*)` с условием `status = 'sold'`.

### Фильтры шаблонов

| Фильтр | Пример | Назначение |
|--------|--------|------------|
| `length` | `{{ venues\|length }}` | количество элементов списка |
| `default` | `{{ venue.name\|default:"Без названия" }}` | значение для пустого поля |
| `date` | `{{ today\|date:"d.m.Y" }}` | формат даты `25.10.2026` |
| `floatformat` | `{{ ticket.price\|floatformat:2 }}` | цена с двумя знаками |
| `capfirst` | `{{ artist.genre\|capfirst }}` | жанр с заглавной буквы |
| `upper` | `{{ ticket.seat\|upper }}` | номер места в верхнем регистре |

Дату программы в формате `дд.мм.гггг` с ПР7 возвращает сам
SQL-запрос (`strftime('%d.%m.%Y', event_date) AS event_day`), поэтому
фильтр `date` применяется к объектам `date`, которые передаёт view
(текущая дата, дата поиска). Значения автоматически экранируются
шаблонизатором.

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

### В веб-интерфейсе — средствами Django ORM (ПР9)

| Операция | ПР7 (SQL) | ПР9 (ORM) |
|----------|-----------|-----------|
| список записей | `SELECT ... ORDER BY` | `Venue.objects.order_by("-capacity", "name")` |
| запись по id | `WHERE id = ?` + проверка `None` | `get_object_or_404(Venue, pk=venue_id)` |
| фильтр по жанру | `WHERE genre = ?` | `.filter(genre=genre)` |
| свободные площадки | подзапрос `NOT IN` | `.exclude(pk__in=busy_venue_ids)` |
| связанные данные | `JOIN ... ON ...` | `select_related("artist", "venue")`, `artist.programs.all()` |
| итоги продаж | `COUNT`, `SUM`, `AVG` | `.aggregate(Count(...), Sum(...), Avg(...))` |
| продажи по программам | `LEFT JOIN`, `GROUP BY` | `.annotate(tickets_sold=Count("tickets", filter=Q(...)))` |
| порог продаж | `HAVING` | `.filter(tickets_sold__gte=min_sold)` после `annotate()` |
| `is_upcoming`, `is_active` | вычисляемые столбцы | методы моделей `Program.is_upcoming()`, `Ticket.is_active()` |

### В веб-интерфейсе — средствами SQL (ПР7, предыдущая реализация)

Операции, которые в ПР3–ПР6 выполнял Python-код, перенесены в
SQL-запросы:

| Операция ПР3 (Python) | ПР7 (SQL) |
|-----------------------|-----------|
| `load_*()` — чтение JSON | `SELECT ... FROM <таблица>` |
| `find_*_by_id()` | `WHERE id = ?` |
| `filter_artists_by_genre()` | `WHERE genre = ?` |
| `filter_venues_by_capacity()` | `WHERE capacity >= ?` |
| `sort_programs_by_date()` | `ORDER BY event_date` |
| `is_venue_available()` | `COUNT(*)` и подзапрос `NOT IN` |
| `count_active_tickets_by_program()` | `COUNT(*) ... WHERE status = 'sold'` |
| связи `program.artist`, `ticket.program` | `JOIN ... ON ...` |
| `Program.is_upcoming()`, `Ticket.is_active()` | вычисляемые столбцы `... AS is_upcoming` |

### Отложены до следующих работ

Операции работают в консольной версии и через ORM (Django shell,
модели `Ticket.cancel()` и т. д.); на веб-страницах появятся вместе с
формами и POST-запросами:

- добавление исполнителя, площадки, программы;
- продажа билета с расчётом цены по промокоду;
- отмена билета, удаление программы.

## Хранение данных

- **Веб-версия (ПР9)** — база Django `db.sqlite3`, таблицы которой
  созданы миграциями; доступ через Django ORM (см. следующий раздел).
- **Исходная база ПР7** — `data/concerts.sqlite`: сохранена без
  изменений как источник данных для переноса в ORM.
- **Консольная версия (ПР3)** — JSON-файлы каталога `data/`:
  `artists.json`, `venues.json`, `programs.json`, `tickets.json`.
  При загрузке: `JSON → dict → объект` с восстановлением связей
  через идентификаторы; при сохранении: `объект → dict → JSON`.
  Эти же файлы — источник данных для импорта в SQLite.

Файл `db.sqlite3` не хранится в репозитории (`.gitignore`): после
клонирования таблицы создаются миграциями, данные переносятся
скриптом или загружаются из fixture (раздел «Запуск приложения»).

## Django ORM (ПР9)

Путь данных в веб-приложении:

```text
view → Django ORM (модель.objects) → SQL → SQLite → объекты моделей → шаблон
```

### Модели

| Модель | Файл | Поля | Таблица |
|--------|------|------|---------|
| `Artist` | `artists/models.py` | `name`, `country` (необяз.), `genre` | `artists_artist` |
| `Venue` | `venues/models.py` | `name`, `address` (необяз.), `capacity` (> 0) | `venues_venue` |
| `Program` | `programs/models.py` | `title`, `artist` (FK), `venue` (FK), `genre`, `event_date` (`DateField`), `base_price` (`DecimalField`) | `programs_program` |
| `Ticket` | `tickets/models.py` | `program` (FK), `seat`, `category` (необяз.), `price` (`DecimalField`), `status` (`sold`/`cancelled`) | `tickets_ticket` |

Первичный ключ `id` Django создаёт сам (`BigAutoField`,
`DEFAULT_AUTO_FIELD`). Необязательные строковые поля объявлены с
`blank=True` и хранят пустую строку вместо `NULL`. Деньги хранятся
в `DecimalField`, дата концерта — в `DateField`.

Методы моделей перенесены из классов ПР3: `Venue.is_suitable_for()`,
`Venue.is_free_on(day)`, `Program.is_upcoming()`, `Ticket.is_active()`,
`Ticket.cancel()` (меняет статус и сохраняет только поле `status`).

Ограничения уровня базы (`Meta.constraints`): вместимость больше 0,
цены не меньше 0, статус билета только `sold` или `cancelled`,
одно место программы нельзя продать дважды — условное ограничение
уникальности `(program, seat)` для `status = 'sold'`, поэтому
отменённый билет место не занимает.

### Связи

```text
Artist 1 ── N Program N ── 1 Venue
              Program 1 ── N Ticket
```

| Поле | Связь | `on_delete` | `related_name` |
|------|-------|-------------|----------------|
| `Program.artist` | многие к одному → `Artist` | `PROTECT` | `artist.programs` |
| `Program.venue` | многие к одному → `Venue` | `PROTECT` | `venue.programs` |
| `Ticket.program` | многие к одному → `Program` | `PROTECT` | `program.tickets` |

`PROTECT` запрещает удалить исполнителя, площадку или программу,
на которые есть ссылки, — история концертов и продаж сохраняется.

### Миграции

```text
python manage.py makemigrations artists venues programs tickets
python manage.py sqlmigrate tickets 0001
python manage.py migrate
python manage.py showmigrations
```

Файлы `*/migrations/0001_initial.py` хранятся в Git. Выбрана
стратегия «таблицы, управляемые Django, и перенос данных»: исходная
база ПР7 не меняется, Django создаёт свои таблицы в `db.sqlite3`.

### Перенос данных из базы ПР7

| Файл | Назначение |
|------|------------|
| `db/inspect_source_db.py` | только чтение: таблицы, столбцы, число записей, проверка битых ссылок |
| `db/import_sqlite_to_orm.py` | перенос `artists → venues → programs → tickets` через `update_or_create()` в одной транзакции `transaction.atomic()` с сохранением id |
| `data/fixtures/concerts.json` | те же данные в формате fixture (`dumpdata`) |

Исходная база открывается в режиме только чтения (`mode=ro`).
Строки дат преобразуются в `date`, цены `REAL` — в `Decimal`,
`NULL` — в пустую строку. Повторный запуск обновляет записи, а не
создаёт дубликаты.

### ORM-запросы проекта

| Вид | Где | Выражение |
|-----|-----|-----------|
| получение набора | `/venues/` | `Venue.objects.order_by("-capacity", "name")` |
| получение объекта | все `*_detail` | `get_object_or_404(Model, pk=...)` |
| фильтр по одному условию | `/artists/?genre=` | `.filter(genre=genre)` |
| фильтр по нескольким условиям | `/tickets/` | цепочка `.filter(program_id=...)`, `.filter(status=...)` |
| фильтр по связанной модели | `/tickets/?venue=` | `.filter(program__venue_id=...)` |
| исключение | `/venues/available/` | `.filter(capacity__gte=...).exclude(pk__in=busy_venue_ids)` |
| поиск по строке | `/artists/?q=` | `.filter(name__lower__contains=q)` |
| поиск по нескольким полям | `/programs/?q=` | `Q(title__...) \| Q(artist__name__...) \| Q(venue__name__...)` |
| сортировка по выбору | `/programs/`, `/tickets/` | словарь `SORT_FIELDS` → `.order_by(...)`, в т. ч. `program__event_date` |
| связанные объекты | афиша, билет | `select_related("artist", "venue")`, `select_related("program__artist", "program__venue")` |
| обратная связь | `/artists/<id>/`, `/venues/<id>/` | `artist.programs...`, `venue.programs...`, `program.tickets...` |
| только нужные поля | подбор площадки, жанры | `values_list("venue_id", flat=True)`, `values_list("genre", flat=True).distinct()` |
| итоговые показатели | статистика | `.aggregate(Count, Sum, Avg)`, `.aggregate(Count, Min, Max)` |
| показатели по группам | статистика, исполнители | `.annotate(Count("tickets", filter=Q(...)), Sum(...))`, `F("venue__name")`, `Coalesce(...)` |
| группировка | статистика | `.values("genre").annotate(Count("pk"), Avg("base_price"))` |
| условие на агрегат | статистика `?min_sold=` | `.filter(tickets_sold__gte=min_sold)` (HAVING) |
| постраничный вывод | `/tickets/?page=` | `Paginator(tickets_list, 5).get_page(...)`, `{% querystring page=... %}` |

Поиск по-русски без учёта регистра. Встроенные `LOWER` и `LIKE` в
SQLite меняют регистр только у латиницы, поэтому `icontains` не
находит «Октябрьский» по запросу «октябрь». В `homepage/apps.py`
при каждом соединении функция `LOWER` заменяется Python-версией
(`str.lower()`), а для строковых полей зарегистрировано
преобразование `Lower`: запрос `name__lower__contains=q.lower()`
выполняется как `LOWER(name) LIKE '%q%'`.

Значения из GET-параметров проверяются: id — `isdigit()`, статус —
по `Ticket.Status.values`, сортировка — только из словаря
`SORT_FIELDS`, номер страницы — `Paginator.get_page()` (на `abc`
вернёт первую страницу, на слишком большой номер — последнюю).

### Администрирование

Модели зарегистрированы в `admin.py` приложений: записи можно
просматривать и изменять на `/admin/` (нужен суперпользователь:
`python manage.py createsuperuser`).

## База данных SQLite (ПР7, предыдущая реализация)

Файлы SQL-слоя сохранены как предыдущая реализация и источник
данных для переноса; представления их больше не используют.

Путь данных в веб-приложении:

```text
SQLite → SQL-запрос → sqlite3 → view → context → шаблон → страница
```

### Структура базы данных

Каждой сущности предметной области соответствует таблица.

**`artists`** — исполнители

| Поле | Тип | Ограничения | Назначение |
|------|-----|-------------|------------|
| `id` | INTEGER | PRIMARY KEY | идентификатор |
| `name` | TEXT | NOT NULL | имя или название коллектива |
| `country` | TEXT | может быть NULL | страна |
| `genre` | TEXT | NOT NULL | жанр |

**`venues`** — площадки

| Поле | Тип | Ограничения | Назначение |
|------|-----|-------------|------------|
| `id` | INTEGER | PRIMARY KEY | идентификатор |
| `name` | TEXT | NOT NULL | название |
| `address` | TEXT | может быть NULL | адрес |
| `capacity` | INTEGER | NOT NULL, CHECK > 0 | вместимость |

**`programs`** — концертные программы

| Поле | Тип | Ограничения | Назначение |
|------|-----|-------------|------------|
| `id` | INTEGER | PRIMARY KEY | идентификатор |
| `title` | TEXT | NOT NULL | название |
| `artist_id` | INTEGER | NOT NULL, FOREIGN KEY → `artists.id` | исполнитель |
| `venue_id` | INTEGER | NOT NULL, FOREIGN KEY → `venues.id` | площадка |
| `genre` | TEXT | NOT NULL | жанр |
| `event_date` | TEXT | NOT NULL | дата `YYYY-MM-DD` |
| `base_price` | REAL | NOT NULL, CHECK >= 0 | базовая цена |

**`tickets`** — билеты

| Поле | Тип | Ограничения | Назначение |
|------|-----|-------------|------------|
| `id` | INTEGER | PRIMARY KEY | идентификатор |
| `program_id` | INTEGER | NOT NULL, FOREIGN KEY → `programs.id` | программа |
| `seat` | TEXT | NOT NULL | место |
| `category` | TEXT | может быть NULL | категория места |
| `price` | REAL | NOT NULL, CHECK >= 0 | цена с учётом скидки |
| `status` | TEXT | NOT NULL, DEFAULT `'sold'`, CHECK in (`sold`, `cancelled`) | статус |

### Первичные и внешние ключи

Поле `id` каждой таблицы — первичный ключ: однозначно определяет
запись, и на него ссылаются другие таблицы. Внешние ключи:

```text
programs.artist_id  → artists.id   (у исполнителя много программ)
programs.venue_id   → venues.id    (на площадке много программ)
tickets.program_id  → programs.id  (на программу много билетов)
```

Проверку внешних ключей SQLite выполняет, только если в соединении
выполнена команда `PRAGMA foreign_keys = ON` — это делает
`get_connection()`. Дата хранится строкой `YYYY-MM-DD`: такой формат
правильно сравнивается и сортируется как текст.

### Файлы слоя базы данных

| Файл | Назначение |
|------|------------|
| `sql/schema.sql` | `CREATE TABLE IF NOT EXISTS` для четырёх таблиц |
| `sql/queries.sql` | 18 проверенных SQL-запросов с комментариями |
| `db/database.py` | `DB_PATH`, `get_connection()` (`row_factory = sqlite3.Row`, `PRAGMA foreign_keys = ON`), `create_schema()`, `fetch_all()`, `fetch_one()` |
| `db/import_json.py` | перенос данных из JSON в SQLite |
| `data/concerts.sqlite` | файл базы данных |

### Создание базы и перенос данных

```text
python -m db.import_json
```

Скрипт создаёт таблицы по `sql/schema.sql`, очищает их и заново
заполняет из JSON-файлов методом `executemany()` с параметрами `?`.
Таблицы заполняются в порядке `artists → venues → programs → tickets`
(сначала те, на которые ссылаются внешние ключи), очищаются — в
обратном. Все вставки — одна транзакция: при ошибке выполняется
`rollback()`, при успехе — `commit()`. Скрипт можно запускать
повторно. Проверка:

```text
sqlite3 data/concerts.sqlite
sqlite> .tables
sqlite> PRAGMA foreign_key_list(programs);
sqlite> SELECT COUNT(*) FROM tickets;
```

### SQL-запросы проекта (`sql/queries.sql`)

| № | Запрос | Вид | Страница |
|---|--------|-----|----------|
| 1 | список исполнителей по алфавиту | выборка | `/artists/` |
| 2 | список площадок по вместимости | выборка, ORDER BY DESC | `/venues/` |
| 3 | жанры без повторов | DISTINCT | `/artists/` (фильтр) |
| 4 | исполнители выбранного жанра | WHERE | `/artists/?genre=` |
| 5 | площадки вместимостью не менее N | WHERE | `/venues/available/` |
| 6 | число программ на площадке в дату | WHERE, COUNT | `/venues/<id>/` |
| 7 | свободные площадки на дату | WHERE, подзапрос NOT IN | `/venues/available/` |
| 8 | афиша программ | JOIN (3 таблицы) | `/programs/` |
| 9 | программы исполнителя | JOIN, WHERE | `/artists/<id>/` |
| 10 | билеты с программой и площадкой | JOIN (3 таблицы) | `/tickets/` |
| 11 | полная информация о билете | JOIN (4 таблицы) | `/tickets/<id>/` |
| 12 | число билетов, выручка, средняя цена | COUNT, SUM, AVG | `/tickets/statistics/` |
| 13 | число программ, мин. и макс. цена | COUNT, MIN, MAX | `/tickets/statistics/` |
| 14 | активные билеты на программу | COUNT, WHERE | `/programs/<id>/` |
| 15 | продажи по программам | LEFT JOIN, GROUP BY | `/tickets/statistics/` |
| 16 | программы по площадкам | LEFT JOIN, GROUP BY | `/tickets/statistics/` |
| 17 | программы и средняя цена по жанрам | GROUP BY, AVG | `/tickets/statistics/` |
| 18 | программы с продажами не менее N | GROUP BY, HAVING | `/tickets/statistics/?min_sold=` |

В файле значения условий заданы для проверки (`WHERE genre =
'классика'`); выполнить все запросы:

```text
sqlite3 data/concerts.sqlite ".read sql/queries.sql"
```

### Получение данных в Django (до ПР9)

Тексты запросов были константами в начале `views.py` каждого приложения
(`VENUE_LIST_SQL`, `AVAILABLE_VENUES_SQL` и т. д.), вместо значений
стоит параметр `?`. View вызывает `fetch_all()` или `fetch_one()`
из `db/database.py` и передаёт строки в шаблон через `context`:

```python
def available_venues(request):
    ...
    venues_list = fetch_all(
        AVAILABLE_VENUES_SQL,
        [capacity, event_date.isoformat()],
    )
```

- `row_factory = sqlite3.Row` — к полям строки обращаются по имени:
  `row["name"]` в Python, `{{ venue.name }}` в шаблоне;
- значения от пользователя (жанр, дата, вместимость, порог) передаются
  только параметрами `?`; f-строки и конкатенация для подстановки
  значений в SQL не используются;
- числа и дата из GET-параметров сначала проверяются
  (`int()`, `date.fromisoformat()`), при ошибке страница показывает
  сообщение и запрос не выполняется.

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
├── sql/                   # SQL-файлы (ПР7)
│   ├── schema.sql         # создание таблиц
│   └── queries.sql        # проверенные запросы
├── db/                    # работа с SQLite из Python (ПР7)
│   ├── __init__.py
│   ├── database.py        # подключение и выполнение запросов
│   ├── import_json.py     # перенос данных из JSON
│   ├── inspect_source_db.py   # инспекция базы ПР7 (ПР9)
│   └── import_sqlite_to_orm.py  # перенос базы ПР7 в ORM (ПР9)
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
│       ├── available.html
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
│   │   ├── statistics.html
│   │   └── includes/ticket_status.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   │   └── 0001_initial.py  # миграция модели (ПР9)
│   ├── models.py          # модель Ticket (ПР9)
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
├── data/                  # JSON-файлы, база ПР7 concerts.sqlite
│   └── fixtures/concerts.json  # данные в формате fixture (ПР9)
├── db.sqlite3             # база Django (не в Git, создаётся migrate)
└── tests/                 # автоматизированные тесты pytest
    ├── conftest.py
    ├── test_database.py
    ├── test_artists.py
    ├── test_venues.py
    ├── test_programs.py
    ├── test_tickets.py
    ├── test_web.py
    └── test_orm.py        # модели, связи, ORM-запросы (ПР9)
```

Все пять приложений имеют одинаковый набор Python-файлов (показан
на примере `tickets/`).

## Назначение модулей

### `concerts/`

Пакет настроек Django-проекта:

- `settings.py` — настройки: `INSTALLED_APPS`, `DEBUG`,
  `ALLOWED_HOSTS`, локализация, каталог шаблонов
  `TEMPLATES["DIRS"]`;
- `urls.py` — маршрутизация верхнего уровня и `handler404`;
- `asgi.py`, `wsgi.py` — точки взаимодействия с сервером.

### `homepage/`

Приложение главной страницы — точки входа в проект:

- `views.py` — view-функции `index()` и `page_not_found()`;
- `apps.py` — Unicode-версия функции `LOWER` для SQLite (поиск
  по-русски без учёта регистра);
- `urls.py` — маршрут главной страницы (`homepage:index`);
- `templates/homepage/` — главная страница и страница 404;
- `static/homepage/` — собственные CSS, JavaScript и логотип.


### `artists/`, `venues/`, `programs/`, `tickets/`

Приложения разделов. В каждом:

- `models.py` — модель раздела (`Artist`, `Venue`, `Program`,
  `Ticket`); `migrations/` — миграции; `admin.py` — регистрация в
  админ-панели;
- `views.py` — view-функции: получают данные через ORM, готовят
  контекст и вызывают `render()`;
- `urls.py` — пространство имён `app_name` и маршруты `list`, `detail`
  (в `venues` также `available`, в `tickets` — `statistics`);
- `templates/<приложение>/` — шаблоны списка, страницы объекта и
  включаемый фрагмент `includes/`;

Отдельное приложение для пользователей не создаётся: в проекте нет
такой сущности, а для учётных записей Django предоставляет
встроенное приложение `django.contrib.auth`.

### `models/`

Классы предметной области и функции работы с коллекциями (ПР3):
`Artist`, `Venue`, `Program`, `Ticket`. Используются консольной
версией. Не путать с моделями Django в файлах `models.py`
приложений.

### `storage.py`, `utils.py`, `main.py`

Хранилище JSON, функции безопасного консольного ввода и консольное
меню. Сохранены с ПР3 и продолжают работать.

### `db/`, `sql/`

Слой базы данных ПР7 (описан в разделе «База данных SQLite») и
скрипты переноса данных в ORM (раздел «Django ORM»).

## Установка зависимостей

```text
pip install -r requirements.txt
```

Состав `requirements.txt`: `Django==5.2.*`, `pytest`, `pytest-django`,
`flake8`.

## Запуск приложения

Веб-версия (Django):

```text
python manage.py migrate
python db/import_sqlite_to_orm.py
python manage.py check
python manage.py runserver
```

`migrate` создаёт таблицы в `db.sqlite3`, скрипт переносит в них
данные из `data/concerts.sqlite` (база ПР7 уже есть в репозитории).
Вместо скрипта данные можно загрузить из fixture:

```text
python manage.py loaddata data/fixtures/concerts.json
```

Пересоздать саму базу ПР7 из JSON-файлов: `python -m db.import_json`.

После запуска открыть в браузере адрес `http://127.0.0.1:8000/`.

Консольная версия (сохранена):

```text
python main.py
```

## Запуск тестов

```text
pytest -v
```

Django в тестах настраивает плагин `pytest-django`
(`DJANGO_SETTINGS_MODULE` в `pytest.ini`). Тесты с фикстурой `db`
работают с отдельной тестовой базой, которую Django создаёт
миграциями и очищает после каждого теста; набор данных создаётся
через ORM фикстурой `sample_data` в `conftest.py`.

Тесты `tests/test_web.py` обращаются к страницам через тестовый
HTTP-клиент Django.
Они проверяют, какие шаблоны использованы (`response.templates`),
наследование от `base.html`, подключение фрагментов `include`,
содержимое контекста, именованные URL, фильтры, обработку пустого
списка, подключение статических файлов и коды ответа 404, а также
страницы ПР7: фильтр по жанру, подбор площадки, статистику, проверку
ввода и передачу значений параметрами.

`tests/test_orm.py` (ПР9) проверяет модели и связи (прямые и
обратные, `PROTECT`, ограничения базы, `cancel()`), CRUD-операции,
соответствие миграций моделям (`makemigrations --check`), поиск по
кириллице без учёта регистра, поиск по нескольким полям, фильтры,
сортировку, пагинацию и сохранение параметров между страницами,
статистику, а также перенос данных из базы ПР7.

`tests/test_database.py` проверяет слой БД: создание таблиц,
внешние ключи и `PRAGMA foreign_keys`, ограничения `CHECK`, доступ к
полям по имени, полноту и повторяемость импорта, откат импорта при
ошибке, состав `sql/queries.sql` и выполнение всех его запросов.

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

Реализовано (ПР7):

- спроектирована база SQLite: таблицы `artists`, `venues`,
  `programs`, `tickets`, первичные и внешние ключи;
- таблицы создаются скриптом `sql/schema.sql`;
- модуль подключения `db/database.py` и импорт `db/import_json.py`;
- данные перенесены из JSON в `data/concerts.sqlite`;
- 18 SQL-запросов в `sql/queries.sql` (выборка, WHERE, JOIN,
  агрегатные функции, GROUP BY, HAVING);
- все страницы получают данные из SQLite, `sqlite3.Row`,
  параметризованные запросы;
- новые страницы: подбор свободной площадки и статистика продаж,
  фильтр исполнителей по жанру, программы исполнителя;
- пункт «Статистика» в навигации.

Реализовано (ПР9):

- модели Django `Artist`, `Venue`, `Program`, `Ticket` со связями
  `ForeignKey` (`on_delete=PROTECT`, `related_name`) и ограничениями;
- миграции `0001_initial` четырёх приложений;
- инспекция базы ПР7 и перенос данных в ORM с сохранением id;
- все представления получают данные через ORM: `get_object_or_404`,
  `filter`/`exclude`, `Q`, `F`, `select_related`, `values`,
  `aggregate`/`annotate`;
- поиск исполнителей и программ (кириллица без учёта регистра),
  выбор сортировки афиши и списка билетов;
- фильтры, сортировка и постраничный вывод списка билетов;
- модели зарегистрированы в админ-панели.

Планируется:

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
  (JSON и классы ПР3) остался прежним;
- в ПР7 изменился источник данных веб-части: JSON → SQLite.
  JSON-файлы, классы и консольная версия ПР3 сохранены; правила
  ПР3 (`is_upcoming`, `is_active`, доступность площадки) выражены
  в SQL-запросах;
- в ПР9 веб-часть перешла с SQL-запросов на Django ORM; правила
  ПР3 снова стали методами классов — теперь моделей Django.
