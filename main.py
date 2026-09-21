import storage
from models import venues as venues_module, tickets as tickets_module, artists as artists_module, \
    programs as programs_module
from utils import input_date, input_float, input_int, input_non_empty

ARTISTS_FILE = "data/artists.json"
VENUES_FILE = "data/venues.json"
PROGRAMS_FILE = "data/programs.json"
TICKETS_FILE = "data/tickets.json"


def show_artists(artists: list[dict]) -> None:
    """Вывести список исполнителей."""
    if not artists:
        print("Список исполнителей пуст.")
        return
    print("--- Исполнители ---")
    for artist in artists:
        print(
            f"[{artist['id']}] {artist['name']} — "
            f"{artist['genre']}, {artist['country']}"
        )


def show_venues(venues: list[dict]) -> None:
    """Вывести список площадок."""
    if not venues:
        print("Список площадок пуст.")
        return
    print("--- Площадки ---")
    for venue in venues:
        print(
            f"[{venue['id']}] {venue['name']}, "
            f"{venue['address']}, до {venue['capacity']} чел."
        )


def show_programs(
        programs: list[dict],
        artists: list[dict],
        venues: list[dict]
) -> None:
    """Вывести список концертных программ."""
    if not programs:
        print("Список программ пуст.")
        return
    print("--- Концертные программы ---")
    for program in programs:
        artist = artists_module.find_artist_by_id(
            artists, program["artist_id"]
        )
        venue = venues_module.find_venue_by_id(
            venues, program["venue_id"]
        )
        artist_name = artist["name"] if artist else "неизвестен"
        venue_name = venue["name"] if venue else "неизвестна"
        print(
            f"[{program['id']}] «{program['title']}» "
            f"({program['genre']}) — {artist_name}, "
            f"{venue_name}, {program['event_date']}, "
            f"базовая цена {program['base_price']} руб."
        )


def show_tickets(
        tickets: list[dict],
        programs: list[dict]
) -> None:
    """Вывести список проданных билетов."""
    if not tickets:
        print("Проданных билетов нет.")
        return
    print("--- Билеты ---")
    for ticket in tickets:
        program = programs_module.find_program_by_id(
            programs, ticket["program_id"]
        )
        title = program["title"] if program else "неизвестна"
        print(
            f"[{ticket['id']}] программа «{title}», "
            f"место {ticket['seat']} ({ticket['category']}), "
            f"{ticket['price']} руб."
        )


def menu_add_artist(artists: list[dict]) -> None:
    """Диалог добавления исполнителя."""
    name = input_non_empty("Имя исполнителя: ")
    country = input_non_empty("Страна: ")
    genre = input_non_empty("Жанр: ")
    artist = artists_module.add_artist(artists, name, country, genre)
    print(f"Исполнитель добавлен с id={artist['id']}")


def menu_add_venue(venues: list[dict]) -> None:
    """Диалог добавления площадки."""
    name = input_non_empty("Название площадки: ")
    address = input_non_empty("Адрес: ")
    capacity = input_int("Вместимость: ")
    venue = venues_module.add_venue(venues, name, address, capacity)
    print(f"Площадка добавлена с id={venue['id']}")


def menu_add_program(
        programs: list[dict],
        artists: list[dict],
        venues: list[dict]
) -> None:
    """Диалог создания концертной программы."""
    title = input_non_empty("Название программы: ")
    show_artists(artists)
    artist_id = input_int("id исполнителя: ")
    show_venues(venues)
    venue_id = input_int("id площадки: ")
    genre = input_non_empty("Жанр: ")
    event_date = input_date("Дата (ДД.ММ.ГГГГ): ")
    base_price = input_float("Базовая цена билета: ")

    status = programs_module.check_program_creation(
        title, artist_id, event_date
    )
    if not status.startswith("Программа"):
        print(status)
        return

    if not tickets_module.is_venue_available(
            programs, venue_id, event_date
    ):
        print(tickets_module.get_booking_status(False))
        return

    program = programs_module.add_program(
        programs, title, artist_id, venue_id,
        genre, event_date, base_price
    )
    print(f"Программа добавлена с id={program['id']}")
    print(tickets_module.get_booking_status(True))


def menu_check_venue(
        programs: list[dict],
        venues: list[dict]
) -> None:
    """Диалог проверки доступности площадки на дату."""
    show_venues(venues)
    venue_id = input_int("id площадки: ")
    event_date = input_date("Дата (ДД.ММ.ГГГГ): ")
    available = tickets_module.is_venue_available(
        programs, venue_id, event_date
    )
    print(tickets_module.get_booking_status(available))


def menu_sell_ticket(
        tickets: list[dict],
        programs: list[dict]
) -> None:
    """Диалог продажи билета."""
    if not programs:
        print("Сначала создайте хотя бы одну программу")
        return
    print("--- Доступные программы ---")
    for program in programs:
        print(f"[{program['id']}] {program['title']}")
    program_id = input_int("id программы: ")
    seat = input_non_empty("Место (например, A12): ")
    category = input_non_empty("Категория (партер/балкон): ")
    promo = input("Промокод (Enter — без скидки): ").strip()
    ticket = tickets_module.create_ticket(
        tickets, programs, program_id, seat, category, promo
    )
    if ticket is None:
        print("Программа с указанным id не найдена")
        return
    print(
        f"Билет продан: id={ticket['id']}, "
        f"цена {ticket['price']} руб."
    )


def menu_cancel_ticket(tickets: list[dict]) -> None:
    """Диалог отмены билета."""
    ticket_id = input_int("id билета для отмены: ")
    if tickets_module.cancel_ticket(tickets, ticket_id):
        print("Билет отменён")
    else:
        print("Билет с указанным id не найден")


def menu_find_programs(programs: list[dict]) -> None:
    """Диалог поиска программ по названию."""
    query = input_non_empty("Подстрока названия: ")
    found = programs_module.find_programs(programs, query)
    if not found:
        print("Ничего не найдено")
        return
    for program in found:
        print(f"[{program['id']}] {program['title']}")


def print_menu() -> None:
    print("\n=== Система управления концертными программами ===")
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
    programs = storage.load_programs(PROGRAMS_FILE)
    tickets = storage.load_tickets(TICKETS_FILE)

    while True:
        print_menu()
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            show_artists(artists)
        elif choice == "2":
            show_venues(venues)
        elif choice == "3":
            show_programs(programs, artists, venues)
        elif choice == "4":
            show_tickets(tickets, programs)
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
