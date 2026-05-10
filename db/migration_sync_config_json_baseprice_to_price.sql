-- Выравнивает config_json.basePrice с колонкой products.price (источник истины для витрины).
-- Выполнить один раз при расхождении после ручных правок или старых миграций.

BEGIN;

UPDATE products
SET config_json = jsonb_set(config_json, '{basePrice}', to_jsonb(round(price)::int), true)
WHERE config_json IS NOT NULL;

COMMIT;
