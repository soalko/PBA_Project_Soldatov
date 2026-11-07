"""Общие фикстуры тестов.

Django настраивает плагин pytest-django (DJANGO_SETTINGS_MODULE
в pytest.ini). Тесты с фикстурой db работают с отдельной тестовой
базой: она создаётся миграциями перед запуском и очищается после
каждого теста, поэтому db.sqlite3 и data/concerts.sqlite не меняются.
"""
from datetime import timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest
from django.test import Client
from django.utils import timezone

from artists.models import Artist
from programs.models import Program
from tickets.models import Ticket
from venues.models import Venue

TODAY = timezone.localdate()
FUTURE = TODAY + timedelta(days=30)


@pytest.fixture
def sample_data(db):
    """Небольшой набор данных, созданный через ORM.

    Исполнитель выступает на двух площадках: «Октябрьский» свободен
    сегодня, на «Арене» сегодня концерт. На первую программу два
    билета, один из них отменён.
    """
    artist = Artist.objects.create(
        pk=1, name="Оркестр «Камертон»", country="Россия", genre="классика",
    )
    hall = Venue.objects.create(
        pk=1, name="Октябрьский", address="СПб", capacity=1500,
    )
    arena = Venue.objects.create(
        pk=2, name="Арена", address="Москва", capacity=6000,
    )
    autumn = Program.objects.create(
        pk=1, title="Симфония осени", artist=artist, venue=hall,
        genre="классика", event_date=FUTURE, base_price=Decimal("2500"),
    )
    evening = Program.objects.create(
        pk=2, title="Вечер классики", artist=artist, venue=arena,
        genre="классика", event_date=TODAY, base_price=Decimal("1800"),
    )
    sold = Ticket.objects.create(
        pk=1, program=autumn, seat="A12", category="партер",
        price=Decimal("2125"),
    )
    cancelled = Ticket.objects.create(
        pk=2, program=autumn, seat="B7", category="балкон",
        price=Decimal("2500"), status=Ticket.Status.CANCELLED,
    )
    return SimpleNamespace(
        artist=artist, hall=hall, arena=arena,
        autumn=autumn, evening=evening,
        sold=sold, cancelled=cancelled,
    )


@pytest.fixture
def client(sample_data):
    """Тестовый HTTP-клиент; страницы читают данные sample_data."""
    return Client()
