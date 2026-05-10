-- Доступ к кнопке «Панель управления» в мини-приложении: users.is_staff = true
-- Назначение: UPDATE users SET is_staff = true WHERE telegram_id = <ваш_id>;

BEGIN;

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS is_staff boolean NOT NULL DEFAULT false;

COMMENT ON COLUMN users.is_staff IS 'Персонал: видимость входа в админку из профиля мини-приложения (не даёт прав без отдельной авторизации админки).';

COMMIT;
