-- ============================================
-- Data migration script: MySQL -> PostgreSQL
-- Project: PC Salon
-- ============================================
--
-- HOW TO USE:
-- 1) Export each MySQL table to CSV (UTF-8, with header row):
--    users.csv, categories.csv, products.csv, orders.csv, order_items.csv, reviews.csv
--
-- 2) Put CSV files into:
--    C:\xampp\htdocs\pc_salon\migration_csv\
--
-- 3) Run this script via psql (not pgAdmin), because it uses \copy:
--    psql -U postgres -h localhost -d pc_salon -f "C:\xampp\htdocs\pc_salon\migrate_from_mysql_to_postgres.sql"
--
-- IMPORTANT:
-- - This script assumes schema is already created from database_schema_postgres.sql
-- - If your CSV has different column names/order, adapt \copy column lists below.

\set ON_ERROR_STOP on

BEGIN;

-- ============================================
-- 1. CLEAN TABLES IN SAFE ORDER
-- ============================================
TRUNCATE TABLE
    reviews,
    order_items,
    orders,
    products,
    categories,
    users
RESTART IDENTITY CASCADE;

COMMIT;

-- ============================================
-- 2. LOAD DATA FROM CSV (dependency order)
-- ============================================
--
-- Notes:
-- - DELIMITER ',' and CSV HEADER are expected.
-- - Empty fields become NULL using NULL ''.

\copy users (id, telegram_id, first_name, last_name, username, phone, full_name, address, created_at, updated_at) FROM 'C:/xampp/htdocs/pc_salon/migration_csv/users.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', NULL '', ENCODING 'UTF8');

\copy categories (id, name, image, display_order, created_at) FROM 'C:/xampp/htdocs/pc_salon/migration_csv/categories.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', NULL '', ENCODING 'UTF8');

\copy products (id, category_id, name, price, image, cpu, gpu, description, is_active, created_at, updated_at) FROM 'C:/xampp/htdocs/pc_salon/migration_csv/products.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', NULL '', ENCODING 'UTF8');

\copy orders (id, user_id, order_number, delivery_type, full_name, phone, address, comment, total_amount, payment_method, payment_status, order_status, created_at, updated_at) FROM 'C:/xampp/htdocs/pc_salon/migration_csv/orders.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', NULL '', ENCODING 'UTF8');

CREATE TEMP TABLE tmp_order_items_import (
    id          integer,
    order_id    integer,
    product_id  integer,
    item_type   varchar(20),
    item_name   varchar(255),
    item_specs  text,
    quantity    integer,
    unit_price  numeric(10, 2),
    total_price numeric(10, 2),
    config_data text,
    created_at  timestamp without time zone
);

\copy tmp_order_items_import (id, order_id, product_id, item_type, item_name, item_specs, quantity, unit_price, total_price, config_data, created_at) FROM 'C:/xampp/htdocs/pc_salon/migration_csv/order_items.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', NULL '', ENCODING 'UTF8');

INSERT INTO order_items (id, order_id, product_id, item_type, item_name, item_specs, quantity, unit_price, total_price, config_data, created_at)
SELECT
    id,
    order_id,
    product_id,
    item_type,
    item_name,
    item_specs,
    quantity,
    unit_price,
    total_price,
    CASE
        WHEN config_data IS NULL THEN NULL
        WHEN btrim(config_data) = '' THEN NULL
        WHEN upper(btrim(config_data)) = 'NULL' THEN NULL
        ELSE config_data::jsonb
    END,
    created_at
FROM tmp_order_items_import;

\copy reviews (id, user_id, order_id, product_id, rating, title, comment, is_published, created_at, updated_at) FROM 'C:/xampp/htdocs/pc_salon/migration_csv/reviews.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', NULL '', ENCODING 'UTF8');

-- ============================================
-- 3. FIX IDENTITY SEQUENCES AFTER MANUAL ID IMPORT
-- ============================================
SELECT setval(
    pg_get_serial_sequence('users', 'id'),
    COALESCE((SELECT MAX(id) FROM users), 1),
    true
);

SELECT setval(
    pg_get_serial_sequence('products', 'id'),
    COALESCE((SELECT MAX(id) FROM products), 1),
    true
);

SELECT setval(
    pg_get_serial_sequence('orders', 'id'),
    COALESCE((SELECT MAX(id) FROM orders), 1),
    true
);

SELECT setval(
    pg_get_serial_sequence('order_items', 'id'),
    COALESCE((SELECT MAX(id) FROM order_items), 1),
    true
);

SELECT setval(
    pg_get_serial_sequence('reviews', 'id'),
    COALESCE((SELECT MAX(id) FROM reviews), 1),
    true
);

-- ============================================
-- 4. QUICK INTEGRITY CHECKS
-- ============================================
SELECT 'users' AS table_name, COUNT(*) AS row_count FROM users
UNION ALL
SELECT 'categories', COUNT(*) FROM categories
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'orders', COUNT(*) FROM orders
UNION ALL
SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL
SELECT 'reviews', COUNT(*) FROM reviews;

-- Optional sanity checks:
-- SELECT COUNT(*) FROM products p LEFT JOIN categories c ON c.id = p.category_id WHERE c.id IS NULL;
-- SELECT COUNT(*) FROM order_items oi LEFT JOIN orders o ON o.id = oi.order_id WHERE o.id IS NULL;
-- SELECT COUNT(*) FROM reviews r WHERE r.rating < 1 OR r.rating > 5;
