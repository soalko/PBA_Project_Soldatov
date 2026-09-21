from datetime import date


def _next_id(programs: list[dict]) -> int:
    """Вернуть следующий свободный идентификатор программы."""
    if not programs:
        return 1
    return max(program["id"] for program in programs) + 1


def check_program_creation(
        title: str,
        artist_id: int | None,
        event_day: date
) -> str:
    """Проверить корректность данных новой программы."""
    if not title.strip():
        return "Ошибка: не указано название программы"
    if artist_id is None:
        return "Ошибка: не указан исполнитель"
    if event_day <= date.today():
        return "Ошибка: дата концерта должна быть в будущем"
    return f"Программа «{title}» успешно создана"


def add_program(
        programs: list[dict],
        title: str,
        artist_id: int,
        venue_id: int,
        genre: str,
        event_date: date,
        base_price: float
) -> dict:
    """Добавить концертную программу в список programs."""
    program = {
        "id": _next_id(programs),
        "title": title,
        "artist_id": artist_id,
        "venue_id": venue_id,
        "genre": genre,
        "event_date": event_date.isoformat(),
        "base_price": base_price,
    }
    programs.append(program)
    return program


def find_program_by_id(
        programs: list[dict],
        program_id: int
) -> dict | None:
    """Найти программу по идентификатору."""
    for program in programs:
        if program["id"] == program_id:
            return program
    return None


def find_programs(programs: list[dict], query: str) -> list[dict]:
    """Найти программы по подстроке названия."""
    query_lower = query.lower()
    return [
        program for program in programs
        if query_lower in program["title"].lower()
    ]


def filter_programs_by_genre(
        programs: list[dict],
        genre: str
) -> list[dict]:
    """Отобрать программы по жанру."""
    genre_lower = genre.lower()
    return [
        program for program in programs
        if program["genre"].lower() == genre_lower
    ]


def sort_programs_by_date(programs: list[dict]) -> list[dict]:
    """Отсортировать программы по дате проведения."""
    return sorted(programs, key=lambda program: program["event_date"])


def remove_program(programs: list[dict], program_id: int) -> bool:
    """Удалить программу по идентификатору.
    Возвращает True, если программа была найдена и удалена.
    """
    program = find_program_by_id(programs, program_id)
    if program is None:
        return False
    programs.remove(program)
    return True
