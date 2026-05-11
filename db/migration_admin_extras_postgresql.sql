-- Изображения товаров в БД, автор промокода, сброс профиля (через API + ensure_* в main.py)

ALTER TABLE products
    ADD COLUMN IF NOT EXISTS image_data bytea NULL,
    ADD COLUMN IF NOT EXISTS image_mime varchar(64) NULL;

ALTER TABLE promo_codes
    ADD COLUMN IF NOT EXISTS creator_telegram_id bigint NULL;

CREATE INDEX IF NOT EXISTS idx_promo_codes_creator ON promo_codes (creator_telegram_id);
