import json
import os

from models import Artist, Program, Ticket, Venue


def _load_json(filename: str) -> list[dict]:
    """Загрузить список словарей из JSON-файла.

    При отсутствии файла или ошибке чтения возвращается
    пустой список, программа не завершается аварийно.
    """
    if not os.path.exists(filename):
        return []
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError) as error:
        print(f"Предупреждение: не удалось прочитать {filename}: "
              f"{error}")
        return []
    if not isinstance(data, list):
        return []
    return data


def _save_json(filename: str, data: list[dict]) -> None:
    """Сохранить список словарей в JSON-файл."""
    directory = os.path.dirname(filename) or "."
    os.makedirs(directory, exist_ok=True)
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    except OSError as error:
        print(f"Ошибка сохранения {filename}: {error}")


def load_artists(filename: str) -> list[Artist]:
    """Загрузить исполнителей и преобразовать в объекты Artist."""
    return [Artist.from_data(row) for row in _load_json(filename)]


def save_artists(filename: str, artists: list[Artist]) -> None:
    """Сохранить объекты Artist в JSON-файл."""
    _save_json(filename, [artist.to_data() for artist in artists])


def load_venues(filename: str) -> list[Venue]:
    """Загрузить площадки и преобразовать в объекты Venue."""
    return [Venue.from_data(row) for row in _load_json(filename)]


def save_venues(filename: str, venues: list[Venue]) -> None:
    """Сохранить объекты Venue в JSON-файл."""
    _save_json(filename, [venue.to_data() for venue in venues])


def load_programs(
        filename: str,
        artists: list[Artist],
        venues: list[Venue],
) -> list[Program]:
    """Загрузить программы и восстановить связи с Artist и Venue."""
    programs: list[Program] = []
    for row in _load_json(filename):
        program = Program.from_data(row, artists, venues)
        if program is not None:
            programs.append(program)
    return programs


def save_programs(filename: str, programs: list[Program]) -> None:
    """Сохранить объекты Program в JSON-файл.

    В JSON записываются идентификаторы связанных объектов
    artist_id и venue_id.
    """
    _save_json(filename, [program.to_data() for program in programs])


def load_tickets(
        filename: str,
        programs: list[Program],
) -> list[Ticket]:
    """Загрузить билеты и восстановить связь с Program."""
    tickets: list[Ticket] = []
    for row in _load_json(filename):
        ticket = Ticket.from_data(row, programs)
        if ticket is not None:
            tickets.append(ticket)
    return tickets


def save_tickets(filename: str, tickets: list[Ticket]) -> None:
    """Сохранить объекты Ticket в JSON-файл.

    В JSON записывается идентификатор program_id.
    """
    _save_json(filename, [ticket.to_data() for ticket in tickets])
