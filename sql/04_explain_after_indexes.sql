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
-- TODO: EXPLAIN (ANALYZE, BUFFERS) ...

\echo '--- Q2 ---'
-- TODO: EXPLAIN (ANALYZE, BUFFERS) ...

\echo '--- Q3 ---'
-- TODO: EXPLAIN (ANALYZE, BUFFERS) ...

-- (Опционально) Q4
-- TODO
