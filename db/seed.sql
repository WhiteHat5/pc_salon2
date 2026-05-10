-- Base seed data for local development/testing
-- Цены и CPU/GPU совпадают с index.html: PRODUCTS_* / PRODUCT_CONFIGS.basePrice (дефолт конфигуратора).
-- Run after schema.sql

BEGIN;

INSERT INTO categories (id, name, image, display_order) VALUES
('4k', '4K Gaming', 'photo/4K.png', 1),
('2k', '2K Gaming', 'photo/2K.png', 2),
('fullhd', 'Full HD Gaming', 'photo/FullHD.png', 3)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    image = EXCLUDED.image,
    display_order = EXCLUDED.display_order;

INSERT INTO products (id, category_id, name, price, image, cpu, gpu, description, is_active)
VALUES
(101, '4k', 'AURUM 4K Pro', 349990.00, 'photo/pc4_1.jpg', 'i9-13900K', 'RTX4090', 'Флагманская сборка для 4K.', true),
(102, '4k', 'AURUM 4K Elite', 299990.00, 'photo/pc4_2.jpg', 'i7-13700K', 'RTX4080', 'Мощная сборка для 4K.', true),
(105, '4k', 'AURUM 4K Streaming', 259990.00, 'photo/pc4_3.jpg', 'i7-14700K', 'RTX4080', '4K гейминг и стриминг.', true),
(103, '4k', 'AURUM 4K Standard', 249990.00, 'photo/pc4_4.jpg', 'R9 7900X', 'RTX4070', 'Сбалансированная сборка для 4K.', true),
(104, '4k', 'AURUM 4K Basic', 199990.00, 'photo/pc4_4.jpg', 'R7 7700X', 'RTX4070', 'Бюджетный вход в 4K.', true),
(201, '2k', 'AURUM 2K Ultra', 239990.00, 'photo/pc2_1.jpg', 'i7-13700KF', 'RTX4080', 'Топовая сборка для 2K.', true),
(202, '2k', 'AURUM 2K Pro', 199990.00, 'photo/pc2_2.jpg', 'R7 7800X3D', 'RTX4070', 'Сборка с X3D для 2K.', true),
(203, '2k', 'AURUM 2K Core', 169990.00, 'photo/pc2_3.jpg', 'i5-13600KF', 'RTX4070', 'Сбалансированная сборка для 2K.', true),
(204, '2k', 'AURUM 2K Starter', 149990.00, 'photo/pc2_4.jpg', 'R5 7600', 'RTX4060', 'Стартовая сборка для 2K.', true),
(301, 'fullhd', 'AURUM FHD Ultra', 139990.00, 'photo/pc_fh1.jpg', 'i5-13400F', 'RTX4060', 'Топовая Full HD сборка.', true),
(302, 'fullhd', 'AURUM FHD Pro', 119990.00, 'photo/pc_fh2.jpg', 'R5 7600', 'RTX4060', 'Full HD с хорошим запасом.', true),
(303, 'fullhd', 'AURUM FHD Core', 99990.00, 'photo/pc_fh3.jpg', 'i5-12400F', 'RTX3060', 'Сбалансированная Full HD сборка.', true),
(304, 'fullhd', 'AURUM FHD Starter', 89990.00, 'photo/pc_fh4.jpg', 'R5 5600', 'RTX3050', 'Бюджетный Full HD.', true)
ON CONFLICT (id) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    price = EXCLUDED.price,
    image = EXCLUDED.image,
    cpu = EXCLUDED.cpu,
    gpu = EXCLUDED.gpu,
    description = EXCLUDED.description,
    is_active = EXCLUDED.is_active;

SELECT setval(
    pg_get_serial_sequence('products', 'id'),
    COALESCE((SELECT MAX(id) FROM products), 1)
);

COMMIT;
