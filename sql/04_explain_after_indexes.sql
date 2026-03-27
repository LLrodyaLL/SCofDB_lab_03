\timing on
\echo '=== AFTER INDEXES ==='

SET max_parallel_workers_per_gather = 0;
SET work_mem = '32MB';
ANALYZE;

-- ============================================
-- TODO:
-- Скопируйте сюда ТО ЖЕ множество запросов из 02_explain_before.sql
-- и выполните EXPLAIN (ANALYZE, BUFFERS) повторно.
-- ============================================

\echo '--- Q1 ---'
-- TODO: EXPLAIN (ANALYZE, BUFFERS) ..
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

\echo '--- Q2 ---'
-- TODO: EXPLAIN (ANALYZE, BUFFERS) ...
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, user_id, status, total_amount, created_at
FROM orders
WHERE status = 'paid'
  AND created_at >= TIMESTAMP '2025-01-01'
  AND created_at < TIMESTAMP '2025-04-01'
ORDER BY created_at DESC
LIMIT 100;

\echo '--- Q3 ---'
-- TODO: EXPLAIN (ANALYZE, BUFFERS) ...
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

-- (Опционально) Q4
-- TODO
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
