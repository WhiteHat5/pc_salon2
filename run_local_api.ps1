# Запуск без XAMPP: один процесс отдаёт API + статику (index.html, /js, /photo, /admin).
# Откройте в браузере: http://127.0.0.1:8000/
# Админка: http://127.0.0.1:8000/admin/products.html
#
# Используется Python из виртуального окружения (.venv или venv), чтобы совпадал с pip install.
$apiRoot = Join-Path $PSScriptRoot "python_api"
Set-Location $apiRoot

$py = $null
foreach ($cand in @(
        (Join-Path $apiRoot ".venv\Scripts\python.exe"),
        (Join-Path $apiRoot "venv\Scripts\python.exe")
    )) {
    if (Test-Path $cand) {
        $py = $cand
        break
    }
}
if (-not $py) {
    Write-Warning "Не найден python_api\.venv\Scripts\python.exe — используется python из PATH."
    $py = "python"
}

& $py -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
