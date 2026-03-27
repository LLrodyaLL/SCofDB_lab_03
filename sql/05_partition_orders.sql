\timing on
\echo '=== PARTITION ORDERS BY DATE ==='

-- ============================================
-- TODO: Реализуйте партиционирование orders по дате
-- ============================================

-- Вариант A (рекомендуется): RANGE по created_at (месяц/квартал)
-- Вариант B: альтернативная разумная стратегия
DROP TABLE IF EXISTS orders_partitioned CASCADE;

-- Шаг 1: Подготовка структуры
-- TODO:
-- - создайте partitioned table (или shadow-таблицу для безопасной миграции)
-- - определите partition key = created_at
CREATE TABLE orders_partitioned (
    id UUID NOT NULL,
    user_id UUID NOT NULL,
    status VARCHAR(32) NOT NULL,
    total_amount NUMERIC(12, 2) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    CONSTRAINT orders_partitioned_total_amount_nonnegative CHECK (total_amount >= 0)
) PARTITION BY RANGE (created_at);

-- Шаг 2: Создание партиций
-- TODO:
-- - создайте набор партиций по диапазонам дат
-- - добавьте DEFAULT partition (опционально)
CREATE TABLE orders_partitioned_2024_q1 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

CREATE TABLE orders_partitioned_2024_q2 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');

CREATE TABLE orders_partitioned_2024_q3 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2024-07-01') TO ('2024-10-01');

CREATE TABLE orders_partitioned_2024_q4 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2024-10-01') TO ('2025-01-01');

CREATE TABLE orders_partitioned_2025_q1 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');

CREATE TABLE orders_partitioned_2025_q2 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2025-04-01') TO ('2025-07-01');

CREATE TABLE orders_partitioned_2025_q3 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2025-07-01') TO ('2025-10-01');

CREATE TABLE orders_partitioned_2025_q4 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2025-10-01') TO ('2026-01-01');

CREATE TABLE orders_partitioned_default PARTITION OF orders_partitioned
    DEFAULT;

-- Шаг 3: Перенос данных
-- TODO:
-- - перенесите данные из исходной таблицы
-- - проверьте количество строк до/после
INSERT INTO orders_partitioned (id, user_id, status, total_amount, created_at)
SELECT id, user_id, status, total_amount, created_at
FROM orders;

\echo '--- Row count check ---'
SELECT 'orders' AS table_name, COUNT(*) AS rows_count FROM orders
UNION ALL
SELECT 'orders_partitioned', COUNT(*) FROM orders_partitioned;

-- Шаг 4: Индексы на партиционированной таблице
-- TODO:
-- - создайте нужные индексы (если требуется)
CREATE INDEX idx_orders_partitioned_user_id_created_at_desc
    ON orders_partitioned USING BTREE (user_id, created_at DESC);

CREATE INDEX idx_orders_partitioned_status_created_at_desc
    ON orders_partitioned USING BTREE (status, created_at DESC);

CREATE INDEX idx_orders_partitioned_created_at_brin
    ON orders_partitioned USING BRIN (created_at);

-- Шаг 5: Проверка
-- TODO:
-- - ANALYZE
-- - проверка partition pruning на запросах по диапазону дат
ANALYZE orders_partitioned;

\echo '--- Partition pruning check ---'
EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*)
FROM orders_partitioned
WHERE created_at >= TIMESTAMP '2025-01-01'
  AND created_at < TIMESTAMP '2025-04-01';
