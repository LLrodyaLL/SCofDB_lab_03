\timing on
\echo '=== AFTER PARTITIONING ==='

SET max_parallel_workers_per_gather = 0;
SET work_mem = '32MB';

-- TODO:
-- Выполните ANALYZE для партиционированной таблицы/таблиц
-- Пример:
-- ANALYZE orders;

-- ============================================
-- TODO:
-- Скопируйте сюда те же запросы, что в:
--   02_explain_before.sql
--   04_explain_after_indexes.sql
-- и выполните EXPLAIN (ANALYZE, BUFFERS) после партиционирования.
-- ============================================

\echo '--- Q1 ---'
-- TODO: EXPLAIN (ANALYZE, BUFFERS) ...

\echo '--- Q2 ---'
-- TODO: EXPLAIN (ANALYZE, BUFFERS) ...

\echo '--- Q3 ---'
-- TODO: EXPLAIN (ANALYZE, BUFFERS) ...

-- (Опционально) Q4
-- TODO
