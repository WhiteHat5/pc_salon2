-- Extended demo seed for local presentations
-- Run after: schema.sql + seed.sql

BEGIN;

-- 1) More products for richer catalog
INSERT INTO products (category_id, name, price, image, cpu, gpu, description, is_active)
VALUES
('4k', 'AURUM 4K Creator', 289990.00, 'photo/pc4_2.jpg', 'Ryzen 9 7950X', 'RTX 4080 SUPER', 'High-end workstation and gaming mix.', true),
('2k', 'AURUM 2K Ultra', 239990.00, 'photo/pc2_2.jpg', 'i7-13700KF', 'RTX 4080 SUPER', 'Performance-focused setup for 2K.', true),
('2k', 'AURUM 2K Silent', 184990.00, 'photo/pc2_3.jpg', 'Ryzen 7 7800X3D', 'RTX 4070 SUPER', 'Low-noise optimized 2K build.', true),
('2k', 'AURUM 2K Studio', 214990.00, 'photo/pc2_4.jpg', 'i7-14700', 'RTX 4070 Ti SUPER', 'Balanced for design and gaming.', true),
('fullhd', 'AURUM Full HD Plus', 124990.00, 'photo/pc_fh2.jpg', 'i5-14400F', 'RTX 4060 Ti', 'High FPS setup for Full HD.', true),
('fullhd', 'AURUM Full HD Energy', 99990.00, 'photo/pc_fh3.jpg', 'Ryzen 5 7500F', 'RTX 4060', 'Efficient budget gaming build.', true),
('fullhd', 'AURUM Full HD OfficePlay', 84990.00, 'photo/pc_fh4.jpg', 'i5-13400', 'RTX 3050', 'Office plus casual gaming.', true),
('fullhd', 'AURUM Full HD Esports', 119990.00, 'photo/pc_fh1.jpg', 'Ryzen 7 5700X', 'RTX 4060', 'Esports-oriented configuration.', true);

-- 2) Demo users
INSERT INTO users (telegram_id, first_name, last_name, username, phone, full_name, address)
VALUES
(700000001, 'Alex', 'Demo', 'alex_demo', '79000000001', 'Alex Demo', 'Moscow, Demo st. 1'),
(700000002, 'Nina', 'Demo', 'nina_demo', '79000000002', 'Nina Demo', 'Saint-Petersburg, Demo st. 2')
ON CONFLICT (telegram_id) DO UPDATE SET
    first_name = EXCLUDED.first_name,
    last_name = EXCLUDED.last_name,
    username = EXCLUDED.username,
    phone = EXCLUDED.phone,
    full_name = EXCLUDED.full_name,
    address = EXCLUDED.address;

-- 3) Demo orders
INSERT INTO orders (user_id, order_number, delivery_type, full_name, phone, address, comment, total_amount, payment_method, payment_status, order_status)
SELECT u.id, 'AURUM-DEMO-0001', 'pickup', 'Alex Demo', '79000000001', NULL, 'Demo order #1', 239990.00, 'cash', 'pending', 'new'
FROM users u
WHERE u.telegram_id = 700000001
ON CONFLICT (order_number) DO UPDATE SET
    total_amount = EXCLUDED.total_amount,
    order_status = EXCLUDED.order_status;

INSERT INTO orders (user_id, order_number, delivery_type, full_name, phone, address, comment, total_amount, payment_method, payment_status, order_status)
SELECT u.id, 'AURUM-DEMO-0002', 'delivery', 'Nina Demo', '79000000002', 'Saint-Petersburg, Demo st. 2', 'Demo order #2', 124990.00, 'card', 'paid', 'confirmed'
FROM users u
WHERE u.telegram_id = 700000002
ON CONFLICT (order_number) DO UPDATE SET
    total_amount = EXCLUDED.total_amount,
    order_status = EXCLUDED.order_status,
    payment_status = EXCLUDED.payment_status;

-- 4) Demo order items
INSERT INTO order_items (order_id, product_id, item_type, item_name, item_specs, quantity, unit_price, total_price, config_data)
SELECT o.id, p.id, 'product', p.name, CONCAT(COALESCE(p.cpu, ''), ' | ', COALESCE(p.gpu, '')), 1, p.price, p.price, NULL
FROM orders o
JOIN products p ON p.name = 'AURUM 2K Ultra'
WHERE o.order_number = 'AURUM-DEMO-0001'
  AND NOT EXISTS (
      SELECT 1
      FROM order_items oi
      WHERE oi.order_id = o.id
        AND oi.item_name = p.name
  );

INSERT INTO order_items (order_id, product_id, item_type, item_name, item_specs, quantity, unit_price, total_price, config_data)
SELECT o.id, p.id, 'product', p.name, CONCAT(COALESCE(p.cpu, ''), ' | ', COALESCE(p.gpu, '')), 1, p.price, p.price, NULL
FROM orders o
JOIN products p ON p.name = 'AURUM Full HD Plus'
WHERE o.order_number = 'AURUM-DEMO-0002'
  AND NOT EXISTS (
      SELECT 1
      FROM order_items oi
      WHERE oi.order_id = o.id
        AND oi.item_name = p.name
  );

-- 5) Demo reviews
INSERT INTO reviews (user_id, order_id, product_id, rating, title, comment, is_published)
SELECT u.id, o.id, p.id, 5, 'Great build', 'Everything works fast and stable.', true
FROM users u
JOIN orders o ON o.user_id = u.id AND o.order_number = 'AURUM-DEMO-0002'
JOIN products p ON p.name = 'AURUM Full HD Plus'
WHERE u.telegram_id = 700000002
  AND NOT EXISTS (
      SELECT 1
      FROM reviews r
      WHERE r.user_id = u.id
        AND r.order_id = o.id
        AND r.product_id = p.id
  );

COMMIT;
