-- Очистка истории пополнений (deposit_history) и сдвиг deposit_history_revision,
-- чтобы клиенты с кэшем в localStorage не вернули старые записи при POST /api/user-state.
-- Замените telegram_id при необходимости.

UPDATE user_state
SET profile_finance =
    jsonb_set(
        jsonb_set(
            COALESCE(profile_finance, '{}'::jsonb),
            '{deposit_history}',
            '[]'::jsonb,
            true
        ),
        '{deposit_history_revision}',
        to_jsonb(
            COALESCE((profile_finance->>'deposit_history_revision')::int, 0) + 1
        ),
        true
    ),
    updated_at = NOW()
WHERE telegram_id = 1104322784;

-- Если историю в БД уже обнулили ранее без revision, выполните только увеличение счётчика:
-- UPDATE user_state
-- SET profile_finance = jsonb_set(
--     COALESCE(profile_finance, '{}'::jsonb),
--     '{deposit_history_revision}',
--     to_jsonb(COALESCE((profile_finance->>'deposit_history_revision')::int, 0) + 1),
--     true
--   ),
--   updated_at = NOW()
-- WHERE telegram_id = 1104322784;
