-- Аудит целостности и «лишних» данных (PostgreSQL, схема pc_salon / python_api).
-- Все запросы только SELECT — безопасно для прогона на проде.
-- Ожидаемые таблицы (11): bonus_ledger, categories, certificate_pending,
--   certificate_redemptions, order_items, orders, products, promo_codes,
--   reviews, user_state, users

-- =============================================================================
-- 0) Снимок: таблицы и число строк
-- =============================================================================
SELECT tablename
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

SELECT 'users' AS tbl, COUNT(*) AS n FROM users
UNION ALL SELECT 'categories', COUNT(*) FROM categories
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'orders', COUNT(*) FROM orders
UNION ALL SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL SELECT 'reviews', COUNT(*) FROM reviews
UNION ALL SELECT 'promo_codes', COUNT(*) FROM promo_codes
UNION ALL SELECT 'user_state', COUNT(*) FROM user_state
UNION ALL SELECT 'certificate_redemptions', COUNT(*) FROM certificate_redemptions
UNION ALL SELECT 'certificate_pending', COUNT(*) FROM certificate_pending
UNION ALL SELECT 'bonus_ledger', COUNT(*) FROM bonus_ledger
ORDER BY tbl;

-- «Лишние» таблицы в public (не из списка проекта) — просмотр, не удалять без анализа
SELECT t.tablename
FROM pg_tables t
WHERE t.schemaname = 'public'
  AND t.tablename NOT IN (
    'users', 'categories', 'products', 'orders', 'order_items', 'reviews',
    'promo_codes', 'user_state', 'certificate_redemptions', 'certificate_pending', 'bonus_ledger'
  )
ORDER BY t.tablename;

-- =============================================================================
-- 1) Ссылки на несуществующие сущности (должно быть 0, если FK включены и данные чистые)
-- =============================================================================

-- Товары без категории
SELECT COUNT(*) AS products_orphan_category
FROM products p
LEFT JOIN categories c ON c.id = p.category_id
WHERE c.id IS NULL;

SELECT p.id, p.name, p.category_id
FROM products p
LEFT JOIN categories c ON c.id = p.category_id
WHERE c.id IS NULL
LIMIT 50;

-- Позиции заказа без заказа (при CASCADE обычно невозможно)
SELECT COUNT(*) AS order_items_orphan_order
FROM order_items oi
LEFT JOIN orders o ON o.id = oi.order_id
WHERE o.id IS NULL;

-- Отзывы: битые product_id / user_id / order_id (часть полей NULL — норма)
SELECT COUNT(*) AS reviews_broken_product
FROM reviews r
LEFT JOIN products p ON p.id = r.product_id
WHERE r.product_id IS NOT NULL AND p.id IS NULL;

SELECT COUNT(*) AS reviews_broken_order
FROM reviews r
LEFT JOIN orders o ON o.id = r.order_id
WHERE r.order_id IS NOT NULL AND o.id IS NULL;

SELECT COUNT(*) AS reviews_broken_user
FROM reviews r
LEFT JOIN users u ON u.id = r.user_id
WHERE r.user_id IS NOT NULL AND u.id IS NULL;

-- Заказы с несуществующим user_id
SELECT COUNT(*) AS orders_broken_user
FROM orders o
LEFT JOIN users u ON u.id = o.user_id
WHERE o.user_id IS NOT NULL AND u.id IS NULL;

-- Сертификаты: order_id указывает на удалённый заказ
SELECT COUNT(*) AS cert_redemptions_broken_order
FROM certificate_redemptions cr
LEFT JOIN orders o ON o.id = cr.order_id
WHERE cr.order_id IS NOT NULL AND o.id IS NULL;

-- Бонусы: битые ссылки
SELECT COUNT(*) AS bonus_ledger_broken_user
FROM bonus_ledger bl
LEFT JOIN users u ON u.id = bl.user_id
WHERE bl.user_id IS NOT NULL AND u.id IS NULL;

SELECT COUNT(*) AS bonus_ledger_broken_order
FROM bonus_ledger bl
LEFT JOIN orders o ON o.id = bl.order_id
WHERE bl.order_id IS NOT NULL AND o.id IS NULL;

-- =============================================================================
-- 2) Логические аномалии (правила из миграций и API)
-- =============================================================================

-- Пользователи без telegram_id и без телефона (нарушит chk_users_contact_required после VALIDATE)
SELECT COUNT(*) AS users_no_contact
FROM users
WHERE telegram_id IS NULL
  AND NULLIF(btrim(COALESCE(phone, '')), '') IS NULL;

-- Дубли telegram_id (уникальный индекс не даст вставку, но проверка на старых данных)
SELECT telegram_id, COUNT(*) AS cnt
FROM users
WHERE telegram_id IS NOT NULL
GROUP BY telegram_id
HAVING COUNT(*) > 1;

-- order_items: тип product, но product_id NULL (или наоборот config/pc с product_id)
SELECT COUNT(*) AS order_items_type_mismatch
FROM order_items
WHERE (item_type = 'product' AND product_id IS NULL)
   OR (item_type IN ('config', 'pc') AND product_id IS NOT NULL);

SELECT oi.id, oi.order_id, oi.item_type, oi.product_id, oi.item_name
FROM order_items oi
WHERE (oi.item_type = 'product' AND oi.product_id IS NULL)
   OR (oi.item_type IN ('config', 'pc') AND oi.product_id IS NOT NULL)
LIMIT 50;

-- Отзыв без order_id и без product_id (после chk_reviews_target_required — не должно пройти VALIDATE)
SELECT COUNT(*) AS reviews_no_target
FROM reviews
WHERE order_id IS NULL AND product_id IS NULL;

-- Заказы без позиций (возможны тестовые — решайте вручную)
SELECT o.id, o.order_number, o.created_at
FROM orders o
WHERE NOT EXISTS (SELECT 1 FROM order_items oi WHERE oi.order_id = o.id)
ORDER BY o.created_at DESC
LIMIT 100;

-- Расхождение суммы заказа и суммы позиций (допускается округление; смотрите крупные расхождения)
SELECT o.id, o.order_number, o.total_amount AS order_total,
       COALESCE(SUM(oi.total_price), 0) AS items_sum,
       ABS(o.total_amount - COALESCE(SUM(oi.total_price), 0)) AS diff
FROM orders o
LEFT JOIN order_items oi ON oi.order_id = o.id
GROUP BY o.id, o.order_number, o.total_amount
HAVING ABS(o.total_amount - COALESCE(SUM(oi.total_price), 0)) > 0.05
ORDER BY diff DESC
LIMIT 50;

-- Промокоды: дубликаты кода (уникальность в таблице — проверка)
SELECT code, COUNT(*) AS cnt
FROM promo_codes
GROUP BY code
HAVING COUNT(*) > 1;

-- =============================================================================
-- 3) user_state и JSON (кэш мини-приложения)
-- =============================================================================

-- Строки с непустой корзиной/финансами — для оценки объёма
SELECT COUNT(*) AS user_state_nonempty_cart
FROM user_state
WHERE cart_items IS NOT NULL AND cart_items::text NOT IN ('[]', 'null');

-- Очень большие jsonb (МБ); при необходимости — точечная чистка cart_configs
SELECT telegram_id,
       pg_column_size(cart_items) + pg_column_size(favorite_ids)
         + pg_column_size(profile_finance) + pg_column_size(cart_configs) AS approx_bytes
FROM user_state
ORDER BY approx_bytes DESC
LIMIT 30;

-- Отрицательный баланс в profile_finance (если ключ есть)
SELECT telegram_id, profile_finance->'balance' AS balance
FROM user_state
WHERE (profile_finance->>'balance') IS NOT NULL
  AND (profile_finance->>'balance')::numeric < 0
LIMIT 50;

-- История пополнений: отрицательные amount в массиве (некорректно для UI)
SELECT telegram_id, profile_finance->'deposit_history' AS dep_hist
FROM user_state
WHERE EXISTS (
  SELECT 1
  FROM jsonb_array_elements(COALESCE(profile_finance->'deposit_history', '[]'::jsonb)) AS e
  WHERE (e->>'amount')::numeric < 0
)
LIMIT 20;

-- =============================================================================
-- 4) bonus_ledger и сертификаты
-- =============================================================================

-- Записи без привязки ни к user_id, ни к telegram_id (возможна устаревшая логика)
SELECT COUNT(*) AS bonus_ledger_no_actor
FROM bonus_ledger
WHERE user_id IS NULL AND telegram_id IS NULL;

-- Дубли активации сертификата (уникальность telegram_id+code — не должно быть)
SELECT telegram_id, code, COUNT(*) AS cnt
FROM certificate_redemptions
GROUP BY telegram_id, code
HAVING COUNT(*) > 1;

-- =============================================================================
-- 5) Ограничения в БД: есть ли NOT VALID (нужно VALIDATE после исправления данных)
-- =============================================================================
SELECT conrelid::regclass AS table_name, conname, convalidated
FROM pg_constraint
WHERE contype = 'c'
  AND connamespace = 'public'::regnamespace
  AND convalidated = false
ORDER BY 1, 2;

-- =============================================================================
-- Дальнейшие шаги (вручную, только после бэкапа):
-- - Исправить строки, где счётчики в п.1–2 > 0
-- - ALTER TABLE ... VALIDATE CONSTRAINT ... для chk_* из migration_data_quality_constraints_postgresql.sql
-- - Оптимизация (по окну обслуживания): VACUUM (ANALYZE); при необходимости REINDEX
-- Не удаляйте таблицы из списка проекта — API на них завязан.
-- =============================================================================
