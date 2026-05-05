-- Base seed data for local development/testing
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

INSERT INTO products (category_id, name, price, image, cpu, gpu, description, is_active)
VALUES
('4k', 'AURUM 4K Extreme', 329990.00, 'photo/pc4_1.jpg', 'i9-14900K', 'RTX 4090', 'Флагманская сборка для 4K-гейминга.', true),
('2k', 'AURUM 2K Pro', 199990.00, 'photo/pc2_1.jpg', 'i7-13700KF', 'RTX 4070 Ti SUPER', 'Оптимальный баланс для 2K.', true),
('fullhd', 'AURUM Full HD Start', 109990.00, 'photo/pc_fh1.jpg', 'i5-13400F', 'RTX 4060', 'Стартовая игровая сборка для Full HD.', true);

COMMIT;
