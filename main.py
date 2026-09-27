import storage

from models import Artist, Program, Ticket, Venue

from models.artists import (
    add_artist,
    find_artist_by_id,
    show_artists,
)
from models.programs import (
    add_program,
    find_program_by_id,
    find_programs,
    show_programs,
)
from models.tickets import (
    cancel_ticket,
    create_ticket,
    get_booking_status,
    is_venue_available,
    show_tickets,
)
from models.venues import (
    add_venue,
    find_venue_by_id,
    show_venues,
)
from utils import (
    input_date,
    input_float,
    input_int,
    input_non_empty,
)

ARTISTS_FILE = "data/artists.json"
VENUES_FILE = "data/venues.json"
PROGRAMS_FILE = "data/programs.json"
TICKETS_FILE = "data/tickets.json"


def menu_add_artist(artists: list[Artist]) -> None:
    """Диалог добавления исполнителя."""
    name = input_non_empty("Имя исполнителя: ")
    country = input_non_empty("Страна: ")
    genre = input_non_empty("Жанр: ")
    artist = add_artist(artists, name, country, genre)
    print(f"Исполнитель добавлен с id={artist.id}")


def menu_add_venue(venues: list[Venue]) -> None:
    """Диалог добавления площадки."""
    name = input_non_empty("Название площадки: ")
    address = input_non_empty("Адрес: ")
    capacity = input_int("Вместимость: ")
    if not Venue.validate_capacity(capacity):
        print("Ошибка: вместимость должна быть положительной")
        return
    venue = add_venue(venues, name, address, capacity)
    print(f"Площадка добавлена с id={venue.id}")


def menu_add_program(
        programs: list[Program],
        artists: list[Artist],
        venues: list[Venue],
) -> None:
    """Диалог создания концертной программы."""
    title = input_non_empty("Название программы: ")
    show_artists(artists)
    artist_id = input_int("id исполнителя: ")
    artist = find_artist_by_id(artists, artist_id)
    show_venues(venues)
    venue_id = input_int("id площадки: ")
    venue = find_venue_by_id(venues, venue_id)
    genre = input_non_empty("Жанр: ")
    event_date = input_date("Дата (ДД.ММ.ГГГГ): ")
    base_price = input_float("Базовая цена билета: ")

    status = Program.validate(title, artist, event_date)
    if not status.startswith("Программа"):
        print(status)
        return
    if venue is None:
        print("Ошибка: площадка не найдена")
        return
    if not is_venue_available(programs, venue_id, event_date):
        print(get_booking_status(False))
        return

    program = add_program(
        programs, title, artist, venue,
        genre, event_date, base_price,
    )
    print(f"Программа добавлена с id={program.id}")
    print(get_booking_status(True))


def menu_check_venue(
        programs: list[Program],
        venues: list[Venue],
) -> None:
    """Диалог проверки доступности площадки на дату."""
    show_venues(venues)
    venue_id = input_int("id площадки: ")
    event_date = input_date("Дата (ДД.ММ.ГГГГ): ")
    available = is_venue_available(programs, venue_id, event_date)
    print(get_booking_status(available))


def menu_sell_ticket(
        tickets: list[Ticket],
        programs: list[Program],
) -> None:
    """Диалог продажи билета."""
    if not programs:
        print("Сначала создайте хотя бы одну программу")
        return
    show_programs(programs)
    program_id = input_int("id программы: ")
    program = find_program_by_id(programs, program_id)
    if program is None:
        print("Программа с указанным id не найдена")
        return
    seat = input_non_empty("Место (например, A12): ")
    category = input_non_empty("Категория (партер/балкон): ")
    promo = input("Промокод (Enter — без скидки): ").strip()
    ticket = create_ticket(
        tickets, program, seat, category, promo,
    )
    print(
        f"Билет продан: id={ticket.id}, "
        f"цена {ticket.price} руб."
    )


def menu_cancel_ticket(tickets: list[Ticket]) -> None:
    """Диалог отмены билета."""
    ticket_id = input_int("id билета для отмены: ")
    if cancel_ticket(tickets, ticket_id):
        print("Билет отменён")
    else:
        print("Билет с указанным id не найден")


def menu_find_programs(programs: list[Program]) -> None:
    """Диалог поиска программ по названию."""
    query = input_non_empty("Подстрока названия: ")
    found = find_programs(programs, query)
    if not found:
        print("Ничего не найдено")
        return
    for program in found:
        print(f"[{program.id}] {program}")


def print_menu() -> None:
    """Вывести главное меню."""
    print()
    print("=== Система управления концертными программами ===")
    print("1. Показать исполнителей")
    print("2. Показать площадки")
    print("3. Показать программы")
    print("4. Показать билеты")
    print("5. Добавить исполнителя")
    print("6. Добавить площадку")
    print("7. Создать программу")
    print("8. Проверить доступность площадки")
    print("9. Продать билет")
    print("10. Отменить билет")
    print("11. Найти программу по названию")
    print("0. Выход")


def main() -> None:
    """Точка запуска приложения."""
    artists = storage.load_artists(ARTISTS_FILE)
    venues = storage.load_venues(VENUES_FILE)
    programs = storage.load_programs(PROGRAMS_FILE, artists, venues)
    tickets = storage.load_tickets(TICKETS_FILE, programs)

    while True:
        print_menu()
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            show_artists(artists)
        elif choice == "2":
            show_venues(venues)
        elif choice == "3":
            show_programs(programs)
        elif choice == "4":
            show_tickets(tickets)
        elif choice == "5":
            menu_add_artist(artists)
        elif choice == "6":
            menu_add_venue(venues)
        elif choice == "7":
            menu_add_program(programs, artists, venues)
        elif choice == "8":
            menu_check_venue(programs, venues)
        elif choice == "9":
            menu_sell_ticket(tickets, programs)
        elif choice == "10":
            menu_cancel_ticket(tickets)
        elif choice == "11":
            menu_find_programs(programs)
        elif choice == "0":
            storage.save_artists(ARTISTS_FILE, artists)
            storage.save_venues(VENUES_FILE, venues)
            storage.save_programs(PROGRAMS_FILE, programs)
            storage.save_tickets(TICKETS_FILE, tickets)
            print("Данные сохранены. До встречи!")
            break
        else:
            print("Неизвестная команда, попробуйте снова")


if __name__ == "__main__":
    main()
