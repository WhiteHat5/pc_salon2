-- Исправление путей к фото Full HD: в проекте есть только pc_fh1.jpg … pc_fh4.jpg,
-- старые сиды ссылались на несуществующие pc1_*.jpg → в карточках показывался один placeholder.
-- Выполните в pgAdmin/psql один раз для уже залитой базы.

UPDATE products SET image = 'photo/pc_fh1.jpg' WHERE image = 'photo/pc1_1.jpg';
UPDATE products SET image = 'photo/pc_fh2.jpg' WHERE image = 'photo/pc1_2.jpg';
UPDATE products SET image = 'photo/pc_fh3.jpg' WHERE image = 'photo/pc1_3.jpg';
UPDATE products SET image = 'photo/pc_fh4.jpg' WHERE image = 'photo/pc1_4.jpg';
UPDATE products SET image = 'photo/pc_fh1.jpg' WHERE image = 'photo/pc1_5.jpg';
