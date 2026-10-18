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


def test_context_contains_domain_objects(client):
    response = client.get("/venues/")
    assert [venue.id for venue in response.context["venues"]] == [1, 2]
    response = client.get("/tickets/2/")
    assert response.context["ticket"].status == "cancelled"


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


def test_date_filter_formats_event_date(client):
    expected = (date.today() + timedelta(days=30)).strftime("%d.%m.%Y")
    assert expected in client.get("/programs/1/").content.decode()


def test_default_filter_for_empty_name(client, tmp_path):
    (tmp_path / "venues.json").write_text(
        '[{"id": 1, "name": "", "address": "", "capacity": 10}]',
        encoding="utf-8",
    )
    html = client.get("/venues/").content.decode()
    assert "Без названия" in html
    assert "адрес не указан" in html


def test_empty_collection_message(client, tmp_path):
    (tmp_path / "artists.json").write_text("[]", encoding="utf-8")
    html = client.get("/artists/").content.decode()
    assert "Список исполнителей пуст." in html
    assert "Всего исполнителей: 0" in html


def test_venue_availability_uses_pr3_logic(client):
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


def test_html_special_characters_are_escaped(client, tmp_path):
    (tmp_path / "artists.json").write_text(
        '[{"id": 1, "name": "<b>AC&DC</b>",'
        ' "country": "Австралия", "genre": "рок"}]',
        encoding="utf-8",
    )
    html = client.get("/artists/1/").content.decode()
    assert "&lt;b&gt;AC&amp;DC&lt;/b&gt;" in html
    assert "<b>AC&DC</b>" not in html


def test_page_function_is_removed():
    assert not hasattr(homepage.views, "page")
