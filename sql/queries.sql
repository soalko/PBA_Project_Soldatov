-- ============================================================
-- Система управления концертными программами: SQL-запросы
-- ============================================================
-- Каждый запрос проверен в SQLite CLI:
--     sqlite3 data/concerts.sqlite
--     sqlite> .read sql/queries.sql
-- Конкретные значения (жанр, вместимость, дата, порог) указаны
-- для проверки. В view-функциях вместо них стоит параметр ?,
-- а значение передаётся отдельно (параметризованный запрос).
-- В скобках после номера — где запрос используется на сайте.

.headers on
.mode column

-- ------------------------------------------------------------
-- Выборка списков
-- ------------------------------------------------------------

-- 1. Список исполнителей по алфавиту (/artists/).
SELECT id,
       name,
       country,
       genre
FROM artists
ORDER BY name;

-- 2. Список площадок, самые вместительные первыми (/venues/).
SELECT id,
       name,
       address,
       capacity
FROM venues
ORDER BY capacity DESC;

-- 3. Жанры исполнителей без повторов — пункты фильтра (/artists/).
SELECT DISTINCT genre
FROM artists
ORDER BY genre;

-- ------------------------------------------------------------
-- Фильтрация WHERE
-- ------------------------------------------------------------

-- 4. Исполнители выбранного жанра (/artists/?genre=классика).
SELECT id,
       name,
       country,
       genre
FROM artists
WHERE genre = 'классика'
ORDER BY name;

-- 5. Площадки, вмещающие не менее 1000 зрителей
--    (/venues/available/, поле «Зрителей не менее»).
SELECT id,
       name,
       capacity
FROM venues
WHERE capacity >= 1000
ORDER BY capacity;

-- 6. Есть ли на площадке программа в указанную дату:
--    0 — площадка свободна (/venues/1/, доступность сегодня).
SELECT COUNT(*) AS programs_count
FROM programs
WHERE venue_id = 1
  AND event_date = '2026-11-20';

-- 7. Свободные площадки на дату с вместимостью не менее N
--    (/venues/available/). Подзапрос выбирает id площадок,
--    занятых в эту дату, NOT IN исключает их из результата.
SELECT id,
       name,
       address,
       capacity
FROM venues
WHERE capacity >= 100
  AND id NOT IN (
      SELECT venue_id
      FROM programs
      WHERE event_date = '2026-11-20'
  )
ORDER BY capacity;

-- ------------------------------------------------------------
-- Соединение таблиц JOIN
-- ------------------------------------------------------------

-- 8. Афиша: программы с именем исполнителя и названием площадки,
--    is_upcoming = 1 для ещё не прошедших (/programs/).
SELECT programs.id,
       programs.title,
       strftime('%d.%m.%Y', programs.event_date) AS event_day,
       programs.event_date > date('now', 'localtime') AS is_upcoming,
       artists.name AS artist_name,
       venues.name AS venue_name
FROM programs
JOIN artists ON programs.artist_id = artists.id
JOIN venues ON programs.venue_id = venues.id
ORDER BY programs.event_date;

-- 9. Программы одного исполнителя с площадками (/artists/1/).
SELECT programs.id,
       programs.title,
       strftime('%d.%m.%Y', programs.event_date) AS event_day,
       venues.name AS venue_name
FROM programs
JOIN venues ON programs.venue_id = venues.id
WHERE programs.artist_id = 1
ORDER BY programs.event_date;

-- 10. Билеты с данными программы и площадки (/tickets/):
--     соединяются три таблицы.
SELECT tickets.id,
       tickets.seat,
       tickets.status = 'sold' AS is_active,
       programs.title AS program_title,
       strftime('%d.%m.%Y', programs.event_date) AS event_day,
       venues.name AS venue_name
FROM tickets
JOIN programs ON tickets.program_id = programs.id
JOIN venues ON programs.venue_id = venues.id
ORDER BY tickets.id;

-- 11. Полная информация о билете (/tickets/1/): четыре таблицы.
SELECT tickets.id,
       tickets.seat,
       tickets.category,
       tickets.price,
       tickets.status = 'sold' AS is_active,
       programs.id AS program_id,
       programs.title AS program_title,
       strftime('%d.%m.%Y', programs.event_date) AS event_day,
       artists.name AS artist_name,
       venues.name AS venue_name
FROM tickets
JOIN programs ON tickets.program_id = programs.id
JOIN artists ON programs.artist_id = artists.id
JOIN venues ON programs.venue_id = venues.id
WHERE tickets.id = 1;

-- ------------------------------------------------------------
-- Агрегатные функции
-- ------------------------------------------------------------

-- 12. Продажи: число активных билетов, выручка и средняя цена
--     (/tickets/statistics/). Отменённые билеты не считаются.
SELECT COUNT(*) AS tickets_sold,
       SUM(price) AS revenue,
       ROUND(AVG(price), 2) AS average_price
FROM tickets
WHERE status = 'sold';

-- 13. Программы: количество, минимальная и максимальная
--     базовая цена (/tickets/statistics/).
SELECT COUNT(*) AS programs_count,
       MIN(base_price) AS min_price,
       MAX(base_price) AS max_price
FROM programs;

-- 14. Количество активных билетов на программу (/programs/1/).
SELECT COUNT(*) AS sold
FROM tickets
WHERE program_id = 1
  AND status = 'sold';

-- ------------------------------------------------------------
-- Группировка GROUP BY и фильтрация групп HAVING
-- ------------------------------------------------------------

-- 15. Продажи по программам (/tickets/statistics/).
--     LEFT JOIN оставляет программы без проданных билетов
--     (у них COUNT = 0), условие status в ON учитывает только
--     активные билеты, COALESCE заменяет NULL-сумму на 0.
SELECT programs.title,
       COUNT(tickets.id) AS tickets_sold,
       COALESCE(SUM(tickets.price), 0.0) AS revenue
FROM programs
LEFT JOIN tickets
       ON tickets.program_id = programs.id
      AND tickets.status = 'sold'
GROUP BY programs.id, programs.title
ORDER BY tickets_sold DESC, programs.title;

-- 16. Количество программ на каждой площадке
--     (/tickets/statistics/).
SELECT venues.name,
       COUNT(programs.id) AS programs_count
FROM venues
LEFT JOIN programs ON programs.venue_id = venues.id
GROUP BY venues.id, venues.name
ORDER BY programs_count DESC, venues.name;

-- 17. Жанры: число программ и средняя базовая цена
--     (/tickets/statistics/).
SELECT genre,
       COUNT(*) AS programs_count,
       ROUND(AVG(base_price), 2) AS average_price
FROM programs
GROUP BY genre
ORDER BY programs_count DESC, genre;

-- 18. Популярные программы: продано не менее 2 билетов
--     (/tickets/statistics/?min_sold=2). WHERE отбирает строки
--     до группировки, HAVING — готовые группы после неё.
SELECT programs.title,
       COUNT(tickets.id) AS tickets_sold
FROM programs
JOIN tickets ON tickets.program_id = programs.id
WHERE tickets.status = 'sold'
GROUP BY programs.id, programs.title
HAVING COUNT(tickets.id) >= 2
ORDER BY tickets_sold DESC, programs.title;
