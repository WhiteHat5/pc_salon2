# PC Salon (AURUM)

Единый актуальный режим проекта: **FastAPI + PostgreSQL**  
(без обязательного XAMPP/PHP в runtime).

## Стек

- Frontend: `index.html` + `js/api.js`
- Backend: `python_api/main.py` (FastAPI)
- DB: PostgreSQL
- Admin UI: `admin/products.html`, `admin/orders.html`

## Быстрый старт

### 1) Установить зависимости Python

```powershell
cd python_api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Настроить окружение

```powershell
copy .env.example .env
```

Заполните `python_api/.env`:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=pc_salon
DB_USER=postgres
DB_PASS=YOUR_PASSWORD
ALLOWED_ORIGINS=*
```

### 3) Поднять БД (pgAdmin)

Выполните по порядку:

1. `db/create_db.sql` (подключение к БД `postgres`)
2. `db/schema.sql` (подключение к БД `pc_salon`)
3. `db/seed.sql`
4. Опционально: `db/seed_more.sql`
5. Проверка: `db/verify.sql`

### 4) Запустить приложение

Из корня проекта:

```powershell
.\run_local_api.ps1
```

## Основные URL

- Сайт: `http://127.0.0.1:8000/`
- Health: `http://127.0.0.1:8000/health`
- API: `http://127.0.0.1:8000/api/categories`
- Админка товары: `http://127.0.0.1:8000/admin/products.html`
- Админка заказы: `http://127.0.0.1:8000/admin/orders.html`

## Важные заметки

- Фронт использует `js/api.js` и по умолчанию работает с `http://127.0.0.1:8000/api`.
- Можно явно переопределить API через `window.API_URL` или `localStorage.API_URL`.
- Текущее состояние проекта очищено от PHP-API слоя и ориентировано на Python backend.

## Полезные документы

- Backend: `python_api/README.md`
- PostgreSQL/pgAdmin: `db/README_PGADMIN.md`
- Публикация через ngrok: `NGROK_SETUP.md`
