# Быстрый запуск mini app через один ngrok-туннель

Ниже сценарий для текущего проекта без VPS и без второго туннеля.

## 1) Запустить Python API (локально)

```powershell
cd C:\xampp\htdocs\pc_salon\python_api
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Проверка:

- `http://127.0.0.1:8000/health`

## 2) Запустить Apache в XAMPP

Проверь:

- `http://localhost/pc_salon/index.html`

## 3) Включить Apache-модули для проксирования (один раз)

В `C:\xampp\apache\conf\httpd.conf` должны быть включены строки:

```apache
LoadModule rewrite_module modules/mod_rewrite.so
LoadModule proxy_module modules/mod_proxy.so
LoadModule proxy_http_module modules/mod_proxy_http.so
LoadModule headers_module modules/mod_headers.so
```

И для директории `htdocs` должно быть:

```apache
AllowOverride All
```

После правок перезапусти Apache.

## 4) Проксирование уже настроено в проекте

В корне проекта создан `C:\xampp\htdocs\pc_salon\.htaccess`:

- все запросы `/pc_salon/api/*` проксируются на `http://127.0.0.1:8000/api/*`

Проверка в браузере:

- `http://localhost/pc_salon/api/health` -> `{"ok": true}`
- `http://localhost/pc_salon/api/categories` -> JSON с категориями

## 5) Очистить старую API-переопределялку (если использовалась)

Если ранее задавал `localStorage.setItem('API_URL', ...)`, сбрось:

```js
localStorage.removeItem('API_URL');
location.reload();
```

Это важно, иначе фронт продолжит ходить на старый URL.

## 6) Поднять один туннель ngrok

```powershell
ngrok http 80
```

Получишь URL вида:

- `https://xxxx.ngrok-free.app`

## 7) Настроить Telegram кнопку

В BotFather укажи:

- `https://xxxx.ngrok-free.app/pc_salon/index.html`

Теперь и фронт, и API идут через один домен:

- фронт: `https://xxxx.ngrok-free.app/pc_salon/index.html`
- API: `https://xxxx.ngrok-free.app/pc_salon/api/*`
