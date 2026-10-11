import os
from datetime import date, timedelta

import django
import pytest
from django.test import Client, override_settings
from django.test.utils import setup_test_environment

import storage
from models import Artist, Program, Ticket, Venue

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "concerts.settings")
django.setup()
# debug=False включает собственную страницу 404 вместо отладочной.
setup_test_environment(debug=False)


@pytest.fixture
def client(tmp_path):
    """Тестовый HTTP-клиент с собственным набором JSON-данных."""
    artist = Artist(1, "Оркестр «Камертон»", "Россия", "классика")
    venues = [
        Venue(1, "Октябрьский", "СПб", 1500),
        Venue(2, "Крокус", "Москва", 6000),
    ]
    programs = [
        Program(
            1, "Симфония осени", artist, venues[0], "классика",
            (date.today() + timedelta(days=30)).isoformat(), 2500.0,
        ),
        Program(
            2, "Вечер классики", artist, venues[1], "классика",
            date.today().isoformat(), 1800.0,
        ),
    ]
    tickets = [
        Ticket(1, programs[0], "A12", "партер", 2125.0),
        Ticket(2, programs[0], "B7", "балкон", 2500.0, "cancelled"),
    ]
    storage.save_artists(str(tmp_path / "artists.json"), [artist])
    storage.save_venues(str(tmp_path / "venues.json"), venues)
    storage.save_programs(str(tmp_path / "programs.json"), programs)
    storage.save_tickets(str(tmp_path / "tickets.json"), tickets)

    with override_settings(DATA_DIR=tmp_path):
        yield Client()
