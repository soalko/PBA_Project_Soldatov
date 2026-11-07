"""Перенос данных из базы ПР7 в таблицы Django ORM.

Исходная база data/concerts.sqlite (ПР7) открывается только на
чтение. Данные записываются через модели в базу Django db.sqlite3,
к которой уже применены миграции (python manage.py migrate).

Запуск из корня проекта:
    python db/import_sqlite_to_orm.py

Скрипт можно запускать повторно: update_or_create() обновляет
запись с тем же id, а не создаёт дубликат.
"""
import os
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

import django

BASE_DIR = Path(__file__).resolve().parent.parent
# Корень проекта в путях поиска модулей: тогда находятся пакет
# настроек concerts и приложения, даже при запуске из каталога db.
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "concerts.settings")
# Django нужно инициализировать до импорта моделей.
django.setup()

from django.db import transaction  # noqa: E402

from artists.models import Artist  # noqa: E402
from db.inspect_source_db import SOURCE_DB, open_read_only  # noqa: E402
from programs.models import Program  # noqa: E402
from tickets.models import Ticket  # noqa: E402
from venues.models import Venue  # noqa: E402


def import_all(source_path=SOURCE_DB):
    """Перенести все записи и вернуть их количество по моделям.

    Порядок повторяет зависимости: исполнители и площадки, затем
    программы (ссылаются на них), затем билеты (ссылаются на
    программы). Исходные id сохраняются, поэтому связи не теряются.
    """
    with open_read_only(source_path) as connection:
        artists = connection.execute(
            "SELECT id, name, country, genre FROM artists ORDER BY id"
        ).fetchall()
        venues = connection.execute(
            "SELECT id, name, address, capacity FROM venues ORDER BY id"
        ).fetchall()
        programs = connection.execute(
            "SELECT id, title, artist_id, venue_id, genre, event_date, "
            "base_price FROM programs ORDER BY id"
        ).fetchall()
        tickets = connection.execute(
            "SELECT id, program_id, seat, category, price, status "
            "FROM tickets ORDER BY id"
        ).fetchall()

    # Все изменения — одной транзакцией: при ошибке в любой записи
    # откатывается весь перенос, частичных данных не остаётся.
    with transaction.atomic():
        for row in artists:
            Artist.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "name": row["name"],
                    # NULL из SQL превращается в пустую строку.
                    "country": row["country"] or "",
                    "genre": row["genre"],
                },
            )
        for row in venues:
            Venue.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "name": row["name"],
                    "address": row["address"] or "",
                    "capacity": row["capacity"],
                },
            )
        for row in programs:
            Program.objects.update_or_create(
                pk=row["id"],
                defaults={
                    # Внешние ключи задаются по id перенесённых записей.
                    "artist_id": row["artist_id"],
                    "venue_id": row["venue_id"],
                    "title": row["title"],
                    "genre": row["genre"],
                    # Строка 'YYYY-MM-DD' -> объект date для DateField.
                    "event_date": date.fromisoformat(row["event_date"]),
                    # REAL -> Decimal через str, без хвостов float.
                    "base_price": Decimal(str(row["base_price"])),
                },
            )
        for row in tickets:
            Ticket.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "program_id": row["program_id"],
                    "seat": row["seat"],
                    "category": row["category"] or "",
                    "price": Decimal(str(row["price"])),
                    "status": row["status"],
                },
            )

    return {
        "artists": Artist.objects.count(),
        "venues": Venue.objects.count(),
        "programs": Program.objects.count(),
        "tickets": Ticket.objects.count(),
    }


def main():
    counts = import_all()
    print("Перенос данных завершён.")
    for name, count in counts.items():
        print(f"{name}: {count}")


if __name__ == "__main__":
    main()
