-- Промокоды (скидка по коду сертификата). Админка: admin/promocodes.html
-- Коды хранятся в ВЕРХНЕМ регистре (как в приложении).

CREATE TABLE IF NOT EXISTS promo_codes (
    id SERIAL PRIMARY KEY,
    code VARCHAR(64) NOT NULL UNIQUE,
    discount_percent NUMERIC(5, 2) NOT NULL CHECK (discount_percent > 0 AND discount_percent <= 100),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    note TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_promo_codes_active ON promo_codes (is_active);

INSERT INTO promo_codes (code, discount_percent, is_active, note)
VALUES
    ('AURUM5', 5, TRUE, 'seed'),
    ('AURUM7', 7, TRUE, 'seed'),
    ('AURUM10', 10, TRUE, 'seed'),
    ('PREMIUM12', 12, TRUE, 'seed'),
    ('VIP15', 15, TRUE, 'seed')
ON CONFLICT (code) DO NOTHING;
