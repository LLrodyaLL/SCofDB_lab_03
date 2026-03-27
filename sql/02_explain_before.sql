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
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, user_id, status, total_amount, created_at
FROM orders
WHERE user_id = (
    SELECT id
    FROM users
    ORDER BY created_at
    LIMIT 1
)
ORDER BY created_at DESC
LIMIT 50;

\echo '--- Q2: Фильтрация по статусу + диапазону дат ---'
-- TODO: Подставьте свой запрос
-- EXPLAIN (ANALYZE, BUFFERS)
-- SELECT ...
-- FROM orders
-- WHERE status = 'paid'
--   AND created_at >= ...
--   AND created_at < ...;
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, user_id, status, total_amount, created_at
FROM orders
WHERE status = 'paid'
  AND created_at >= TIMESTAMP '2025-01-01'
  AND created_at < TIMESTAMP '2025-04-01'
ORDER BY created_at DESC
LIMIT 100;


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
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    o.user_id,
    COUNT(DISTINCT o.id) AS orders_count,
    SUM(oi.price * oi.quantity) AS revenue
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
WHERE o.created_at >= TIMESTAMP '2025-01-01'
  AND o.created_at < TIMESTAMP '2026-01-01'
GROUP BY o.user_id
ORDER BY revenue DESC
LIMIT 20;


-- (Опционально) Q4: полный агрегат по периоду, который сложно ускорить индексами
\echo '--- Q4: Полный агрегат по периоду ---'
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    date_trunc('month', created_at) AS month,
    COUNT(*) AS orders_count,
    SUM(total_amount) AS revenue
FROM orders
WHERE created_at >= TIMESTAMP '2024-01-01'
  AND created_at < TIMESTAMP '2026-01-01'
GROUP BY date_trunc('month', created_at)
ORDER BY month;
