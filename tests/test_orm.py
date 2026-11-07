"""ПР9: модели Django, связи, миграции и запросы через ORM."""
import sqlite3
from datetime import timedelta
from decimal import Decimal
from io import StringIO

import pytest
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.utils import timezone

import db.database
from artists.models import Artist
from db import import_sqlite_to_orm
from programs.models import Program
from tickets.models import Ticket
from venues.models import Venue

TODAY = timezone.localdate()
FUTURE = TODAY + timedelta(days=30)

# ---------------------------------------------------------------
# Модели, связи и ограничения
# ---------------------------------------------------------------


def test_models_have_str(sample_data):
    assert str(sample_data.artist) == "Оркестр «Камертон»"
    assert str(sample_data.hall) == "Октябрьский"
    assert str(sample_data.autumn).startswith("Симфония осени (")
    assert str(sample_data.sold) == "Билет №1: Симфония осени, место A12"


def test_forward_relations(sample_data):
    ticket = Ticket.objects.select_related("program__venue").get(pk=1)
    assert ticket.program.title == "Симфония осени"
    assert ticket.program.venue.name == "Октябрьский"
    # Столбец внешнего ключа доступен как program_id.
    assert ticket.program_id == 1


def test_reverse_relations_use_related_name(sample_data):
    assert set(sample_data.artist.programs.all()) == {
        sample_data.autumn, sample_data.evening,
    }
    assert list(sample_data.arena.programs.all()) == [sample_data.evening]
    assert sample_data.autumn.tickets.count() == 2


def test_protect_keeps_related_records(sample_data):
    # У площадки есть программы: удаление запрещено.
    with pytest.raises(ProtectedError):
        sample_data.hall.delete()
    with pytest.raises(ProtectedError):
        sample_data.autumn.delete()


def test_ticket_cancel_and_status(sample_data):
    ticket = sample_data.sold
    assert ticket.is_active() is True
    ticket.cancel()
    ticket.refresh_from_db()
    assert ticket.status == Ticket.Status.CANCELLED
    assert ticket.is_active() is False


def test_program_is_upcoming(sample_data):
    assert sample_data.autumn.is_upcoming() is True
    assert sample_data.evening.is_upcoming() is False


def test_venue_methods(sample_data):
    assert sample_data.hall.is_suitable_for(1500) is True
    assert sample_data.hall.is_suitable_for(1501) is False
    assert sample_data.hall.is_free_on(TODAY) is True
    assert sample_data.arena.is_free_on(TODAY) is False


def test_database_checks_constraints(sample_data):
    with pytest.raises(IntegrityError), transaction.atomic():
        Venue.objects.create(name="Пустой зал", capacity=0)
    with pytest.raises(IntegrityError), transaction.atomic():
        Ticket.objects.create(
            program=sample_data.autumn, seat="Z1", price=Decimal("-1"),
        )


def test_seat_can_be_sold_once(sample_data):
    # Место A12 уже продано на эту программу.
    with pytest.raises(IntegrityError), transaction.atomic():
        Ticket.objects.create(
            program=sample_data.autumn, seat="A12", price=Decimal("100"),
        )
    # Место B7 было отменено, его можно продать снова.
    Ticket.objects.create(
        program=sample_data.autumn, seat="B7", price=Decimal("100"),
    )
    assert sample_data.autumn.tickets.filter(seat="B7").count() == 2


def test_crud_operations(db):
    venue = Venue.objects.create(name="Клуб", address="", capacity=200)
    assert Venue.objects.filter(pk=venue.pk).exists()

    venue.capacity = 250
    venue.save()
    assert Venue.objects.get(pk=venue.pk).capacity == 250

    Venue.objects.filter(pk=venue.pk).update(name="Клуб «Подвал»")
    assert Venue.objects.get(pk=venue.pk).name == "Клуб «Подвал»"

    venue.delete()
    with pytest.raises(Venue.DoesNotExist):
        Venue.objects.get(pk=venue.pk)


def test_migrations_match_models(db):
    # makemigrations --check завершается ошибкой, если модели
    # изменены, а миграции для них не созданы.
    call_command(
        "makemigrations", "--check", "--dry-run", stdout=StringIO(),
    )


# ---------------------------------------------------------------
# Поиск, фильтрация и сортировка
# ---------------------------------------------------------------


def test_artist_search_ignores_case_for_cyrillic(client):
    Artist.objects.create(name="Группа «Северный ветер»", genre="рок")
    for query in ("ветер", "ВЕТЕР", "Ветер"):
        response = client.get("/artists/", {"q": query})
        names = [artist.name for artist in response.context["artists"]]
        assert names == ["Группа «Северный ветер»"], query


def test_artist_list_counts_programs(client):
    Artist.objects.create(name="Без программ", genre="рок")
    response = client.get("/artists/")
    counts = {a.name: a.programs_count for a in response.context["artists"]}
    assert counts == {"Без программ": 0, "Оркестр «Камертон»": 2}


@pytest.mark.parametrize(
    "query, titles",
    [
        ("осени", ["Симфония осени"]),  # название программы
        ("камертон", ["Вечер классики", "Симфония осени"]),  # исполнитель
        ("арена", ["Вечер классики"]),  # площадка
        ("нет такого", []),
    ],
)
def test_program_search_in_several_fields(client, query, titles):
    response = client.get("/programs/", {"q": query})
    assert [p.title for p in response.context["programs"]] == titles


def test_program_sort_by_price_and_unknown_value(client):
    response = client.get("/programs/", {"sort": "-price"})
    prices = [p.base_price for p in response.context["programs"]]
    assert prices == sorted(prices, reverse=True)
    response = client.get("/programs/", {"sort": "id; DROP TABLE"})
    assert response.context["sort"] == "date"
    assert response.context["programs"][0].event_date == TODAY


def add_tickets(program, count, start_price=100):
    for number in range(count):
        Ticket.objects.create(
            program=program,
            seat=f"N{number}",
            price=Decimal(start_price + number),
        )


def test_ticket_filters_combine_conditions(client, sample_data):
    add_tickets(sample_data.evening, 2)
    response = client.get("/tickets/", {"venue": "1"})
    assert [t.pk for t in response.context["tickets"]] == [1, 2]
    response = client.get("/tickets/", {"venue": "1", "status": "sold"})
    assert [t.pk for t in response.context["tickets"]] == [1]
    response = client.get("/tickets/", {"program": "2"})
    assert response.context["page_obj"].paginator.count == 2


def test_ticket_filters_ignore_bad_values(client):
    response = client.get(
        "/tickets/", {"venue": "abc", "status": "lost", "sort": "x"},
    )
    assert response.status_code == 200
    assert response.context["page_obj"].paginator.count == 2
    assert response.context["sort"] == "id"


def test_ticket_sort_by_price(client, sample_data):
    add_tickets(sample_data.evening, 2, start_price=3000)
    response = client.get("/tickets/", {"sort": "-price"})
    prices = [t.price for t in response.context["tickets"]]
    assert prices == sorted(prices, reverse=True)


# ---------------------------------------------------------------
# Пагинация
# ---------------------------------------------------------------


def test_ticket_pagination(client, sample_data):
    add_tickets(sample_data.evening, 10)  # всего 12 билетов
    response = client.get("/tickets/")
    page = response.context["page_obj"]
    assert page.paginator.num_pages == 3
    assert len(page.object_list) == 5
    html = response.content.decode()
    assert "Далее" in html

    last = client.get("/tickets/", {"page": "3"}).context["page_obj"]
    assert len(last.object_list) == 2
    assert not last.has_next()


@pytest.mark.parametrize("page, number", [("abc", 1), ("999", 3)])
def test_bad_page_number_is_handled(client, sample_data, page, number):
    add_tickets(sample_data.evening, 10)
    response = client.get("/tickets/", {"page": page})
    assert response.status_code == 200
    assert response.context["page_obj"].number == number


def test_pagination_keeps_filters(client, sample_data):
    add_tickets(sample_data.evening, 10)
    html = client.get(
        "/tickets/", {"venue": "2", "sort": "price"},
    ).content.decode()
    assert "?venue=2&amp;sort=price&amp;page=2" in html


# ---------------------------------------------------------------
# Статистика (aggregate / annotate)
# ---------------------------------------------------------------


def test_statistics_aggregates(client, sample_data):
    context = client.get("/tickets/statistics/").context
    assert context["sales"] == {
        "tickets_sold": 1,
        "revenue": Decimal("2125"),
        "average_price": Decimal("2125"),
    }
    assert context["prices"]["min_price"] == Decimal("1800")
    assert context["prices"]["max_price"] == Decimal("2500")


def test_statistics_by_program_without_sales_is_zero(client):
    rows = list(client.get("/tickets/statistics/").context["by_program"])
    assert rows[-1] == {
        "title": "Вечер классики",
        "venue_name": "Арена",
        "tickets_sold": 0,
        "revenue": Decimal("0"),
    }


def test_statistics_empty_database(db):
    from django.test import Client

    context = Client().get("/tickets/statistics/").context
    assert context["sales"]["tickets_sold"] == 0
    assert context["sales"]["revenue"] is None
    assert list(context["by_program"]) == []


# ---------------------------------------------------------------
# Перенос данных из базы ПР7
# ---------------------------------------------------------------


@pytest.fixture
def source_db(tmp_path, monkeypatch):
    """Маленькая исходная база ПР7 во временном каталоге."""
    path = tmp_path / "source.sqlite"
    monkeypatch.setattr(db.database, "DB_PATH", path)
    conn = db.database.get_connection()
    db.database.create_schema(conn)
    conn.execute("INSERT INTO artists VALUES (7, 'Хор', NULL, 'классика')")
    conn.execute("INSERT INTO venues VALUES (3, 'Зал', NULL, 300)")
    conn.execute(
        "INSERT INTO programs VALUES (5, 'Гала', 7, 3, 'классика', ?, 99.9)",
        [FUTURE.isoformat()],
    )
    conn.execute(
        "INSERT INTO tickets VALUES (9, 5, 'A1', NULL, 50.5, 'cancelled')"
    )
    conn.commit()
    conn.close()
    return path


def test_import_keeps_ids_and_relations(db, source_db):
    counts = import_sqlite_to_orm.import_all(source_db)
    assert counts == {"artists": 1, "venues": 1, "programs": 1, "tickets": 1}

    ticket = Ticket.objects.select_related("program__artist").get(pk=9)
    assert ticket.program.pk == 5
    assert ticket.program.artist.name == "Хор"
    assert ticket.program.event_date == FUTURE
    assert ticket.program.base_price == Decimal("99.90")
    assert ticket.status == Ticket.Status.CANCELLED
    # NULL из исходной базы стал пустой строкой.
    assert ticket.category == ""
    assert Venue.objects.get(pk=3).address == ""


def test_import_can_be_repeated(db, source_db):
    first = import_sqlite_to_orm.import_all(source_db)
    second = import_sqlite_to_orm.import_all(source_db)
    assert first == second


def test_import_does_not_change_source(db, source_db):
    before = source_db.read_bytes()
    import_sqlite_to_orm.import_all(source_db)
    assert source_db.read_bytes() == before


def test_import_missing_source(db, tmp_path):
    with pytest.raises(FileNotFoundError):
        import_sqlite_to_orm.import_all(tmp_path / "missing.sqlite")


def test_source_is_opened_read_only(source_db):
    conn = import_sqlite_to_orm.open_read_only(source_db)
    with pytest.raises(sqlite3.OperationalError):
        conn.execute("DELETE FROM tickets")
    conn.close()


def test_views_do_not_use_sql_layer():
    for app in ("artists", "venues", "programs", "tickets"):
        path = db.database.BASE_DIR / app / "views.py"
        code = path.read_text(encoding="utf-8")
        assert "fetch_all" not in code and "sqlite3" not in code, app


def test_program_dates_are_compared_as_dates(sample_data):
    later = Program.objects.filter(event_date__gt=TODAY)
    assert list(later) == [sample_data.autumn]
    soon = TODAY + timedelta(days=1)
    assert Program.objects.filter(event_date__range=(TODAY, soon)).count() == 1
