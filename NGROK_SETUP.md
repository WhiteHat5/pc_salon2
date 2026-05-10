# Быстрый запуск mini app через один ngrok-туннель

Актуальный сценарий для текущего проекта: **только FastAPI + PostgreSQL**, без Apache/XAMPP.

## 1) Запустить приложение локально (UI + API)

Из корня проекта:

```powershell
cd C:\xampp\htdocs\pc_salon
.\run_local_api.ps1
```

Или напрямую:

```powershell
cd C:\xampp\htdocs\pc_salon\python_api
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Проверка:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/api/categories`

## 2) Очистить старое переопределение API URL (если использовалось)

Если раньше задавался внешний/старый backend через localStorage:

```js
localStorage.removeItem('API_URL');
location.reload();
```

## 3) Поднять ngrok на порт FastAPI

```powershell
ngrok http 8000
```

Получите URL вида:

- `https://xxxx.ngrok-free.app`

## 4) Настроить Telegram Mini App

В BotFather для кнопки/веб-аппа укажите:

- `https://xxxx.ngrok-free.app/`

Теперь всё идет через один домен:

- фронт: `https://xxxx.ngrok-free.app/`
- API: `https://xxxx.ngrok-free.app/api/*`
- админка: `https://xxxx.ngrok-free.app/admin/products.html` и `.../admin/orders.html`

## 5) Примечание про `.htaccess`

Файл `.htaccess` можно оставить как исторический/опциональный артефакт.  
В текущем режиме FastAPI он не требуется для работы mini app.
