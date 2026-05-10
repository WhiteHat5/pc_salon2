-- Data quality patch for PostgreSQL (FastAPI runtime).
-- Goal: keep NULL only where it is logically valid.
--
-- Apply after:
--   1) db/schema.sql
--   2) db/migration_certificates_bonus_postgresql.sql (optional, but recommended)

BEGIN;

-- ------------------------------------------------------------
-- 1) users: at least one contact identifier must be present
--    (telegram_id OR non-empty phone)
-- ------------------------------------------------------------
ALTER TABLE users
    DROP CONSTRAINT IF EXISTS chk_users_contact_required;

ALTER TABLE users
    ADD CONSTRAINT chk_users_contact_required
    CHECK (
        telegram_id IS NOT NULL
        OR NULLIF(btrim(COALESCE(phone, '')), '') IS NOT NULL
    ) NOT VALID;

-- ------------------------------------------------------------
-- 2) order_items: strict relation between item_type and product_id
--    - product -> product_id required
--    - config/pc -> product_id must be NULL
-- ------------------------------------------------------------
-- Normalize legacy rows first to avoid migration failure.
UPDATE order_items
SET item_type = 'pc'
WHERE item_type = 'product'
  AND product_id IS NULL;

ALTER TABLE order_items
    DROP CONSTRAINT IF EXISTS chk_order_items_type_product_link;

ALTER TABLE order_items
    ADD CONSTRAINT chk_order_items_type_product_link
    CHECK (
        (item_type = 'product' AND product_id IS NOT NULL)
        OR
        (item_type IN ('config', 'pc') AND product_id IS NULL)
    ) NOT VALID;

-- ------------------------------------------------------------
-- 3) reviews: review must be attached to order or product
-- ------------------------------------------------------------
ALTER TABLE reviews
    DROP CONSTRAINT IF EXISTS chk_reviews_target_required;

ALTER TABLE reviews
    ADD CONSTRAINT chk_reviews_target_required
    CHECK (
        order_id IS NOT NULL
        OR product_id IS NOT NULL
    ) NOT VALID;

COMMIT;

-- Validate constraints after transaction commit.
-- (Validation can take time on large datasets, so keep it explicit.)
ALTER TABLE users
    VALIDATE CONSTRAINT chk_users_contact_required;

ALTER TABLE order_items
    VALIDATE CONSTRAINT chk_order_items_type_product_link;

ALTER TABLE reviews
    VALIDATE CONSTRAINT chk_reviews_target_required;

