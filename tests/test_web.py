import pytest


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


def test_pages_share_common_layout(client):
    for url in ("/", "/venues/", "/tickets/1/"):
        html = client.get(url).content.decode()
        assert html.startswith("<!DOCTYPE html>")
        assert "bootstrap@5.3.3" in html
        assert 'href="/programs/"' in html


def test_index_links_to_sections(client):
    html = client.get("/").content.decode()
    for url in ("/artists/", "/venues/", "/programs/", "/tickets/"):
        assert f'href="{url}"' in html


def test_page_title_comes_from_object(client):
    html = client.get("/venues/2/").content.decode()
    assert "<title>Крокус</title>" in html


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
