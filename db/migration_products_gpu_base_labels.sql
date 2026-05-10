-- Привести поле gpu к «базовым» обозначениям без Ti / SUPER (как в index.html: PRODUCTS_*).
-- Безопасно для уже заполненной БД: только UPDATE по name, id не меняются.
-- Проверьте имена товаров — они должны совпадать с вашей таблицей products.

BEGIN;

UPDATE products SET gpu = 'RTX4070' WHERE name = 'AURUM 4K Standard';

UPDATE products SET gpu = 'RTX4080' WHERE name = 'AURUM 4K Creator';

UPDATE products SET gpu = 'RTX4080' WHERE name = 'AURUM 2K Ultra';

UPDATE products SET gpu = 'RTX4070' WHERE name = 'AURUM 2K Pro';

UPDATE products SET gpu = 'RTX4070' WHERE name = 'AURUM 2K Studio';

UPDATE products SET gpu = 'RTX4060' WHERE name = 'AURUM Full HD Plus';

COMMIT;
