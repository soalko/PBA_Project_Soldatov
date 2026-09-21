from datetime import date, datetime


def input_int(prompt: str) -> int:
    """Запросить у пользователя целое число."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Ошибка: введите целое число")


def input_float(prompt: str) -> float:
    """Запросить у пользователя число с плавающей точкой."""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Ошибка: введите число")


def input_date(prompt: str) -> date:
    """Запросить у пользователя дату в формате ДД.ММ.ГГГГ."""
    while True:
        raw = input(prompt)
        try:
            return datetime.strptime(raw, "%d.%m.%Y").date()
        except ValueError:
            print("Ошибка: неверный формат даты, ожидается ДД.ММ.ГГГГ")


def input_non_empty(prompt: str) -> str:
    """Запросить непустую строку."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Ошибка: строка не может быть пустой")
