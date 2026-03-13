\timing on
\echo '=== BEFORE OPTIMIZATION ==='

-- Рекомендуемые настройки для сравнимых замеров
SET max_parallel_workers_per_gather = 0;
SET work_mem = '32MB';
ANALYZE;

-- ============================================
-- TODO: Добавьте не менее 3 запросов
-- Для каждого обязательно: EXPLAIN (ANALYZE, BUFFERS)
-- ============================================

\echo '--- Q1: Фильтрация + сортировка (пример класса запроса) ---'
-- TODO: Подставьте свой запрос
-- Пример класса:
-- EXPLAIN (ANALYZE, BUFFERS)
-- SELECT ...
-- FROM orders
-- WHERE ...
-- ORDER BY created_at DESC
-- LIMIT ...;

\echo '--- Q2: Фильтрация по статусу + диапазону дат ---'
-- TODO: Подставьте свой запрос
-- EXPLAIN (ANALYZE, BUFFERS)
-- SELECT ...
-- FROM orders
-- WHERE status = 'paid'
--   AND created_at >= ...
--   AND created_at < ...;

\echo '--- Q3: JOIN + GROUP BY ---'
-- TODO: Подставьте свой запрос
-- EXPLAIN (ANALYZE, BUFFERS)
-- SELECT ...
-- FROM orders o
-- JOIN order_items oi ON oi.order_id = o.id
-- WHERE ...
-- GROUP BY ...
-- ORDER BY ...
-- LIMIT ...;

-- (Опционально) Q4: полный агрегат по периоду, который сложно ускорить индексами
