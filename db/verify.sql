-- Quick validation queries after create_db + schema + seed

-- 1) Table list
SELECT tablename
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

-- 2) Row counts
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

-- 3) FK integrity sanity checks (all should be 0)
SELECT COUNT(*) AS broken_products_category
FROM products p
LEFT JOIN categories c ON c.id = p.category_id
WHERE c.id IS NULL;

SELECT COUNT(*) AS broken_order_items_order
FROM order_items oi
LEFT JOIN orders o ON o.id = oi.order_id
WHERE o.id IS NULL;

SELECT COUNT(*) AS broken_reviews_product
FROM reviews r
LEFT JOIN products p ON p.id = r.product_id
WHERE r.product_id IS NOT NULL AND p.id IS NULL;
