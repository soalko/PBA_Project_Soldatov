import json
import os


def _load_json(filename: str) -> list[dict]:
    """Загрузить список записей из JSON-файла."""
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
    """Сохранить список записей в JSON-файл."""
    directory = os.path.dirname(filename) or "."
    os.makedirs(directory, exist_ok=True)
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    except OSError as error:
        print(f"Ошибка сохранения {filename}: {error}")


def load_artists(filename: str) -> list[dict]:
    """Загрузить исполнителей из JSON-файла."""
    return _load_json(filename)


def save_artists(filename: str, artists: list[dict]) -> None:
    """Сохранить исполнителей в JSON-файл."""
    _save_json(filename, artists)


def load_venues(filename: str) -> list[dict]:
    """Загрузить площадки из JSON-файла."""
    return _load_json(filename)


def save_venues(filename: str, venues: list[dict]) -> None:
    """Сохранить площадки в JSON-файл."""
    _save_json(filename, venues)


def load_programs(filename: str) -> list[dict]:
    """Загрузить концертные программы из JSON-файла."""
    return _load_json(filename)


def save_programs(filename: str, programs: list[dict]) -> None:
    """Сохранить концертные программы в JSON-файл."""
    _save_json(filename, programs)


def load_tickets(filename: str) -> list[dict]:
    """Загрузить билеты из JSON-файла."""
    return _load_json(filename)


def save_tickets(filename: str, tickets: list[dict]) -> None:
    """Сохранить билеты в JSON-файл."""
    _save_json(filename, tickets)
