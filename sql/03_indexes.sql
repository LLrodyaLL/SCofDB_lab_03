\timing on
\echo '=== APPLY INDEXES ==='

-- ============================================
-- TODO: Создайте индексы на основе ваших EXPLAIN ANALYZE
-- ============================================

-- Индекс 1
-- TODO:
-- CREATE INDEX ... ON ... USING BTREE (...);
-- Обоснование:
-- - какой запрос ускоряет
-- - почему выбран именно этот тип индекса
CREATE INDEX IF NOT EXISTS idx_orders_user_id_created_at_desc
    ON orders USING BTREE (user_id, created_at DESC);

-- Индекс 2
-- TODO:
-- CREATE INDEX ... ON ... USING ... (...);
-- Обоснование:
-- - какой запрос ускоряет
-- - почему выбран именно этот тип индекса
CREATE INDEX IF NOT EXISTS idx_orders_status_created_at_desc
    ON orders USING BTREE (status, created_at DESC);

-- Индекс 3
-- TODO:
-- CREATE INDEX ... ON ... USING ... (...);
-- Обоснование:
-- - какой запрос ускоряет
-- - почему выбран именно этот тип индекса
CREATE INDEX IF NOT EXISTS idx_orders_created_at_brin
    ON orders USING BRIN (created_at);


-- (Опционально) Частичный индекс / BRIN / составной индекс
-- TODO

-- Не забудьте обновить статистику после создания индексов
-- TODO:
-- ANALYZE;

ANALYZE;
