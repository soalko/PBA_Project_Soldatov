from datetime import date

program_title = "Симфония осени"
artist_name = "Оркестр «Камертон»"
venue_name = "Концертный зал «Октябрьский»"
venue_capacity = 1500
tickets_sold_str = "980"          # приходит из формы как строка
event_date = date(2026, 11, 20)
base_ticket_price = 2500.0
is_venue_booked = False
promo_code = "AUTUMN15"


# ---------- Функция 1. Создание концертной программы ----------
def check_program_creation(title, artist, event_day):
    today = date.today()
    if title == "":
        return "Ошибка: не указано название программы"
    if artist == "":
        return "Ошибка: не указан исполнитель"
    if event_day <= today:
        return "Ошибка: дата концерта должна быть в будущем"
    return f"Программа «{title}» успешно создана"


# ---------- Функция 2. Проверка доступности площадки ----------
def check_venue_availability(booked, capacity, sold_str):
    sold = int(sold_str)
    free_seats = capacity - sold
    if booked:
        return "Площадка уже занята в этот день"
    if free_seats <= 0:
        return "Свободных мест нет"
    return f"Площадка доступна, свободных мест: {free_seats}"


# ---------- Функция 3. Расчёт стоимости билета ----------
def calculate_ticket_price(base_price, code):
    discount = 0.0
    if code == "AUTUMN15":
        discount = 0.15
    elif code == "STUDENT":
        discount = 0.30
    else:
        discount = 0.0
    final_price = base_price * (1 - discount)
    return round(final_price, 2)


print("Концертная программа")
print(f"Название:     {program_title}")
print(f"Исполнитель:  {artist_name}")
print(f"Площадка:     {venue_name} (вместимость {venue_capacity} чел.)")
print(f"Дата:         {event_date}\n")

print("1)", check_program_creation(program_title, artist_name, event_date))
print("2)", check_venue_availability(is_venue_booked, venue_capacity, tickets_sold_str))
print(f"3) Стоимость билета с промокодом «{promo_code}»: "
      f"{calculate_ticket_price(base_ticket_price, promo_code)} руб.")