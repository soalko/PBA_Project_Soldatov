-- ============================================================
-- Система управления концертными программами: структура БД
-- ============================================================
-- Таблицы создаются в порядке зависимостей: сначала те, на которые
-- ссылаются другие (artists, venues), затем programs и tickets.
-- IF NOT EXISTS позволяет выполнять скрипт повторно без ошибки.

-- Исполнители.
CREATE TABLE IF NOT EXISTS artists (
    id      INTEGER PRIMARY KEY,
    name    TEXT NOT NULL,
    country TEXT,                     -- страна может быть не указана
    genre   TEXT NOT NULL
);

-- Концертные площадки.
CREATE TABLE IF NOT EXISTS venues (
    id       INTEGER PRIMARY KEY,
    name     TEXT NOT NULL,
    address  TEXT,                    -- адрес может быть не указан
    capacity INTEGER NOT NULL CHECK (capacity > 0)
);

-- Концертные программы: исполнитель выступает на площадке в дату.
CREATE TABLE IF NOT EXISTS programs (
    id         INTEGER PRIMARY KEY,
    title      TEXT NOT NULL,
    artist_id  INTEGER NOT NULL,
    venue_id   INTEGER NOT NULL,
    genre      TEXT NOT NULL,
    event_date TEXT NOT NULL,         -- дата в формате YYYY-MM-DD
    base_price REAL NOT NULL CHECK (base_price >= 0),
    FOREIGN KEY (artist_id) REFERENCES artists (id),
    FOREIGN KEY (venue_id) REFERENCES venues (id)
);

-- Билеты на программу. Отменённый билет не удаляется,
-- а получает статус 'cancelled' (как метод Ticket.cancel() из ПР3).
CREATE TABLE IF NOT EXISTS tickets (
    id         INTEGER PRIMARY KEY,
    program_id INTEGER NOT NULL,
    seat       TEXT NOT NULL,
    category   TEXT,                  -- категория места необязательна
    price      REAL NOT NULL CHECK (price >= 0),
    status     TEXT NOT NULL DEFAULT 'sold'
               CHECK (status IN ('sold', 'cancelled')),
    FOREIGN KEY (program_id) REFERENCES programs (id)
);
