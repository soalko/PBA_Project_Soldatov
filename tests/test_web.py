from datetime import date, timedelta

import pytest
from django.urls import reverse

import homepage.views


@pytest.mark.parametrize(
    "url, text",
    [
        ("/", "Система управления концертными программами"),
        ("/artists/", "Оркестр «Камертон»"),
        ("/artists/1/", "Россия"),
        ("/venues/", "Октябрьский"),
        ("/venues/1/", "1500 мест"),
        ("/programs/", "Симфония осени"),
        ("/programs/1/", "Оркестр «Камертон»"),
        ("/tickets/", "Билет №1"),
        ("/tickets/1/", "A12"),
    ],
)
def test_page_is_available(client, url, text):
    response = client.get(url)
    assert response.status_code == 200
    assert text in response.content.decode()


@pytest.mark.parametrize(
    "url, template",
    [
        ("/", "homepage/index.html"),
        ("/artists/", "artists/artist_list.html"),
        ("/artists/1/", "artists/artist_detail.html"),
        ("/venues/", "venues/venue_list.html"),
        ("/venues/1/", "venues/venue_detail.html"),
        ("/programs/", "programs/program_list.html"),
        ("/programs/1/", "programs/program_detail.html"),
        ("/tickets/", "tickets/ticket_list.html"),
        ("/tickets/1/", "tickets/ticket_detail.html"),
    ],
)
def test_page_uses_template_inherited_from_base(client, url, template):
    names = [t.name for t in client.get(url).templates]
    assert names[0] == template
    assert "base.html" in names
    assert "includes/navigation.html" in names


@pytest.mark.parametrize(
    "url, include",
    [
        ("/artists/", "artists/includes/artist_card.html"),
        ("/venues/", "venues/includes/venue_card.html"),
        ("/programs/", "programs/includes/program_status.html"),
        ("/programs/1/", "programs/includes/program_status.html"),
        ("/tickets/", "tickets/includes/ticket_status.html"),
        ("/tickets/1/", "tickets/includes/ticket_status.html"),
    ],
)
def test_repeated_fragments_are_included(client, url, include):
    names = [t.name for t in client.get(url).templates]
    assert include in names


def test_context_contains_rows_from_database(client):
    response = client.get("/venues/")
    # Площадки упорядочены SQL-запросом по убыванию вместимости.
    assert [venue["id"] for venue in response.context["venues"]] == [2, 1]
    response = client.get("/tickets/2/")
    assert response.context["ticket"]["is_active"] == 0


def test_pages_share_common_layout(client):
    for url in ("/", "/venues/", "/tickets/1/"):
        html = client.get(url).content.decode()
        assert html.lstrip().startswith("<!DOCTYPE html>")
        assert "bootstrap@5.3.3" in html
        assert 'href="/programs/"' in html
        assert 'id="current-year"' in html


def test_static_files_are_connected(client):
    html = client.get("/").content.decode()
    assert 'href="/static/homepage/css/style.css"' in html
    assert 'src="/static/homepage/js/main.js"' in html
    assert 'src="/static/homepage/img/logo.png"' in html


def test_static_files_exist():
    from django.contrib.staticfiles import finders

    for path in (
        "homepage/css/style.css",
        "homepage/js/main.js",
        "homepage/img/logo.png",
    ):
        assert finders.find(path) is not None


def test_named_urls_use_namespaces():
    assert reverse("homepage:index") == "/"
    assert reverse("artists:list") == "/artists/"
    assert reverse("venues:detail", args=[2]) == "/venues/2/"
    assert reverse("programs:detail", args=[1]) == "/programs/1/"
    assert reverse("tickets:list") == "/tickets/"


def test_index_links_to_sections(client):
    html = client.get("/").content.decode()
    for url in ("/artists/", "/venues/", "/programs/", "/tickets/"):
        assert f'href="{url}"' in html


def test_page_title_comes_from_object(client):
    html = client.get("/venues/2/").content.decode()
    assert "Крокус – Концертные программы" in html


def test_list_shows_count_with_length_filter(client):
    assert "Всего площадок: 2" in client.get("/venues/").content.decode()
    assert "Всего билетов: 2" in client.get("/tickets/").content.decode()


def test_event_date_is_formatted(client):
    expected = (date.today() + timedelta(days=30)).strftime("%d.%m.%Y")
    assert expected in client.get("/programs/1/").content.decode()


def test_default_filter_for_empty_name(client, run_sql):
    run_sql("UPDATE venues SET name = '', address = NULL WHERE id = 1")
    html = client.get("/venues/").content.decode()
    assert "Без названия" in html
    assert "адрес не указан" in html


def test_empty_collection_message(client, run_sql):
    # Из-за внешних ключей сначала удаляются зависимые записи.
    run_sql("DELETE FROM tickets")
    run_sql("DELETE FROM programs")
    run_sql("DELETE FROM artists")
    html = client.get("/artists/").content.decode()
    assert "Список исполнителей пуст." in html
    assert "Всего исполнителей: 0" in html


def test_venue_availability_from_database(client):
    # На площадке 2 сегодня проходит программа, площадка 1 свободна.
    assert "свободна" in client.get("/venues/1/").content.decode()
    assert "занята" in client.get("/venues/2/").content.decode()


def test_program_detail_shows_related_objects(client):
    html = client.get("/programs/1/").content.decode()
    assert 'href="/artists/1/"' in html
    assert 'href="/venues/1/"' in html
    assert "предстоит" in html
    # Из двух билетов на программу один отменён.
    assert "<strong>Активных билетов:</strong> 1" in html


def test_ticket_status_badges(client):
    assert "активен" in client.get("/tickets/1/").content.decode()
    assert "отменён" in client.get("/tickets/2/").content.decode()


@pytest.mark.parametrize(
    "url, text",
    [
        ("/artists/999/", "Исполнитель не найден"),
        ("/venues/999/", "Площадка не найдена"),
        ("/programs/999/", "Программа не найдена"),
        ("/tickets/999/", "Билет не найден"),
    ],
)
def test_unknown_id_returns_404(client, url, text):
    response = client.get(url)
    assert response.status_code == 404
    assert text in response.content.decode()


@pytest.mark.parametrize("url", ["/nonexistent/", "/venues/abc/"])
def test_unknown_url_uses_custom_404_page(client, url):
    response = client.get(url)
    assert response.status_code == 404
    assert "404 – страница не найдена" in response.content.decode()


def test_html_special_characters_are_escaped(client, run_sql):
    run_sql("UPDATE artists SET name = ? WHERE id = 1", ["<b>AC&DC</b>"])
    html = client.get("/artists/1/").content.decode()
    assert "&lt;b&gt;AC&amp;DC&lt;/b&gt;" in html
    assert "<b>AC&DC</b>" not in html


def test_page_function_is_removed():
    assert not hasattr(homepage.views, "page")


# ---------------------------------------------------------------
# ПР7: страницы получают данные из SQLite
# ---------------------------------------------------------------


def test_page_shows_current_database_data(client, run_sql):
    run_sql("UPDATE venues SET name = 'Октябрьский (обновлено)' WHERE id = 1")
    assert "Октябрьский (обновлено)" in client.get("/venues/").content.decode()


def test_program_list_joins_artist_and_venue(client):
    html = client.get("/programs/").content.decode()
    assert "Оркестр «Камертон» · Октябрьский" in html
    assert "Оркестр «Камертон» · Крокус" in html


def test_ticket_pages_join_related_tables(client):
    assert "Октябрьский" in client.get("/tickets/").content.decode()
    html = client.get("/tickets/1/").content.decode()
    assert "Оркестр «Камертон»" in html
    assert 'href="/programs/1/"' in html


def test_artist_detail_lists_artist_programs(client):
    html = client.get("/artists/1/").content.decode()
    assert "Симфония осени" in html
    assert "Вечер классики" in html


def test_artist_genre_filter(client):
    response = client.get("/artists/", {"genre": "классика"})
    assert len(response.context["artists"]) == 1
    response = client.get("/artists/", {"genre": "рок"})
    assert "Список исполнителей пуст." in response.content.decode()


def test_artist_genre_list_uses_distinct(client):
    response = client.get("/artists/")
    assert [row["genre"] for row in response.context["genres"]] == [
        "классика",
    ]


def test_user_input_is_passed_as_parameter(client):
    # Строка с SQL-кодом сравнивается с genre как обычное значение
    # и не меняет условие запроса.
    response = client.get("/artists/", {"genre": "' OR '1'='1"})
    assert response.status_code == 200
    assert len(response.context["artists"]) == 0


def test_available_venues_page_without_date_shows_form(client):
    response = client.get("/venues/available/")
    assert response.status_code == 200
    assert response.context["searched"] is False
    assert 'name="date"' in response.content.decode()


def test_available_venues_excludes_busy_venue(client):
    today = date.today().isoformat()
    response = client.get("/venues/available/", {"date": today})
    names = [venue["name"] for venue in response.context["venues"]]
    # На площадке «Крокус» сегодня проходит программа.
    assert names == ["Октябрьский"]


def test_available_venues_filters_by_capacity(client):
    future = (date.today() + timedelta(days=60)).isoformat()
    response = client.get(
        "/venues/available/",
        {"date": future, "capacity": "2000"},
    )
    names = [venue["name"] for venue in response.context["venues"]]
    assert names == ["Крокус"]


def test_available_venues_empty_result_message(client):
    today = date.today().isoformat()
    response = client.get(
        "/venues/available/",
        {"date": today, "capacity": "5000"},
    )
    assert "подходящих свободных площадок нет" in response.content.decode()


@pytest.mark.parametrize(
    "params, error",
    [
        ({"date": "20.11.2026"}, "Дата должна быть"),
        ({"date": "2026-11-20", "capacity": "много"}, "целым числом"),
        ({"date": "2026-11-20", "capacity": "-5"}, "меньше 0"),
    ],
)
def test_available_venues_validates_input(client, params, error):
    response = client.get("/venues/available/", params)
    assert error in response.content.decode()
    assert response.context["searched"] is False


def test_statistics_page(client):
    response = client.get("/tickets/statistics/")
    assert response.status_code == 200
    names = [t.name for t in response.templates]
    assert names[0] == "tickets/statistics.html"
    assert "base.html" in names
    # Отменённый билет не учитывается.
    assert response.context["sales"]["tickets_sold"] == 1
    assert response.context["sales"]["revenue"] == 2125.0


def test_statistics_keeps_programs_without_sales(client):
    rows = client.get("/tickets/statistics/").context["by_program"]
    sold = {row["title"]: row["tickets_sold"] for row in rows}
    assert sold == {"Симфония осени": 1, "Вечер классики": 0}


def test_statistics_groups_by_venue_and_genre(client):
    context = client.get("/tickets/statistics/").context
    assert len(context["by_venue"]) == 2
    assert context["by_genre"][0]["programs_count"] == 2


def test_statistics_having_threshold(client):
    response = client.get("/tickets/statistics/", {"min_sold": "1"})
    assert [r["title"] for r in response.context["popular"]] == [
        "Симфония осени",
    ]
    response = client.get("/tickets/statistics/", {"min_sold": "2"})
    assert response.context["popular"] == []
    assert "не менее 2 билетов" in response.content.decode()


def test_statistics_invalid_threshold(client):
    response = client.get("/tickets/statistics/", {"min_sold": "abc"})
    assert "целым числом" in response.content.decode()
    assert response.context["min_sold"] == 2


def test_navigation_links_to_new_pages(client):
    assert reverse("venues:available") == "/venues/available/"
    assert reverse("tickets:statistics") == "/tickets/statistics/"
    html = client.get("/").content.decode()
    assert 'href="/tickets/statistics/"' in html
    assert 'href="/venues/available/"' in client.get(
        "/venues/"
    ).content.decode()
