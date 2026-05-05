# Запуск без XAMPP: один процесс отдаёт API + статику (index.html, /js, /photo, /admin).
# Откройте в браузере: http://127.0.0.1:8000/
# Админка: http://127.0.0.1:8000/admin/products.html (пароль как раньше: admin123)
Set-Location $PSScriptRoot\python_api
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
