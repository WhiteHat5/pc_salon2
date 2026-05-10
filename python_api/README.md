# Python backend (FastAPI)

## 1) Setup

```bash
cd python_api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 2) Environment

```bash
copy .env.example .env
```

Edit `python_api/.env` and set your PostgreSQL password in `DB_PASS`.

## 3) Run (без Apache/XAMPP)

Из корня проекта:

```powershell
.\run_local_api.ps1
```

Или из папки `python_api`:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Сайт: `http://127.0.0.1:8000/` — отдаётся `index.html`, статика `/js`, `/photo`, админка `/admin/`.

## 4) Test

- Health: `http://127.0.0.1:8000/health`
- Categories: `http://127.0.0.1:8000/api/categories`
- Products: `http://127.0.0.1:8000/api/products`

## 5) Frontend

При открытии мини-приложения с порта **8000** `js/api.js` сам использует тот же origin (`/api`). Для нестандартного URL задайте `window.API_URL` или `localStorage.API_URL`.
