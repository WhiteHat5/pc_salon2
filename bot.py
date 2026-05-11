"""
Единый Telegram-бот AURUM: тот же TELEGRAM_BOT_TOKEN, что у FastAPI;
обработка чата для менеджеров (users.is_staff): заказы за сегодня / вчера / дату.

Переменные окружения (python_api/.env или окружение процесса):
  TELEGRAM_BOT_TOKEN — токен от @BotFather
  TELEGRAM_MANAGER_BOT_TOKEN — запасной ключ, если основной не задан
  DB_* — как у API

Запуск из корня проекта (рядом с index.html):
  python bot.py
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Optional
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from psycopg import connect
from psycopg.rows import dict_row

MSK = ZoneInfo("Europe/Moscow")

_ROOT = Path(__file__).resolve().parent
load_dotenv(_ROOT / "python_api" / ".env", override=False)
load_dotenv(override=False)


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


DB = {
    "host": _env("DB_HOST", "localhost"),
    "port": int(_env("DB_PORT", "5432")),
    "dbname": _env("DB_NAME", "pc_salon"),
    "user": _env("DB_USER", "postgres"),
    "password": _env("DB_PASS", ""),
}


def db_conn():
    return connect(**DB, row_factory=dict_row)


def is_staff(telegram_id: int) -> bool:
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT 1 FROM users WHERE telegram_id = %s AND is_staff = true LIMIT 1",
            (telegram_id,),
        )
        return cur.fetchone() is not None


def fetch_orders_day(target: date) -> list[dict[str, Any]]:
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, order_number, full_name, phone, total_amount, order_status,
                   payment_status, delivery_type, created_at
            FROM orders
            WHERE created_at::date = %s
            ORDER BY created_at DESC
            LIMIT 80
            """,
            (target,),
        )
        return list(cur.fetchall())


def format_orders_message(rows: list[dict[str, Any]], title: str) -> str:
    if not rows:
        return f"{title}\n\nЗаказов нет."
    lines = [title, ""]
    for r in rows:
        num = r.get("order_number") or f"#{r.get('id')}"
        st = r.get("order_status") or ""
        amt = r.get("total_amount")
        created = r.get("created_at")
        if hasattr(created, "strftime"):
            ts = created.strftime("%H:%M")
        else:
            ts = str(created)[:16]
        lines.append(f"• {num} · {st} · {amt} ₽ · {ts}")
    lines.append("")
    lines.append("Подробности — в веб-админке «Заказы».")
    return "\n".join(lines)


def tg_api(method: str, payload: dict[str, Any], token: str) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/{method}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def send_message(token: str, chat_id: int, text: str, reply_markup: Optional[dict] = None) -> None:
    body: dict[str, Any] = {"chat_id": chat_id, "text": text}
    if reply_markup:
        body["reply_markup"] = reply_markup
    tg_api("sendMessage", body, token)


MANAGER_KEYBOARD = {
    "keyboard": [
        [{"text": "📋 Заказы за сегодня"}],
        [{"text": "📅 Заказы за вчера"}],
        [{"text": "✏️ Другая дата (ДД.ММ.ГГГГ)"}],
    ],
    "resize_keyboard": True,
}

DATE_RE = re.compile(r"^\s*(\d{1,2})\.(\d{1,2})\.(\d{4})\s*$")


def resolve_bot_token() -> str:
    return _env("TELEGRAM_BOT_TOKEN") or _env("TELEGRAM_MANAGER_BOT_TOKEN")


def main() -> None:
    token = resolve_bot_token()
    if len(token) < 30:
        raise SystemExit("Задайте TELEGRAM_BOT_TOKEN в окружении (.env).")

    offset = 0
    waiting_date: dict[int, bool] = {}

    print("[aurum_bot] long polling… меню заказов для is_staff")

    while True:
        try:
            url = f"https://api.telegram.org/bot{token}/getUpdates?timeout=50&offset={offset}"
            with urllib.request.urlopen(url, timeout=55) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            print("getUpdates error:", exc)
            time.sleep(3)
            continue

        if not data.get("ok"):
            print("Telegram API:", data)
            time.sleep(2)
            continue

        for upd in data.get("result", []):
            offset = max(offset, int(upd["update_id"]) + 1)
            msg = upd.get("message") or upd.get("edited_message")
            if not msg:
                continue
            chat = msg.get("chat") or {}
            chat_id = int(chat.get("id"))
            from_user = msg.get("from") or {}
            uid = from_user.get("id")
            if uid is None:
                continue
            uid = int(uid)
            text = (msg.get("text") or "").strip()

            if not is_staff(uid):
                send_message(token, chat_id, "Старт)")
                continue

            if text in ("/start", "/menu"):
                waiting_date.pop(chat_id, None)
                send_message(
                    token,
                    chat_id,
                    "Меню менеджера: выберите период или отправьте дату.",
                    MANAGER_KEYBOARD,
                )
                continue

            today_msk = datetime.now(MSK).date()

            if text == "📋 Заказы за сегодня":
                waiting_date.pop(chat_id, None)
                rows = fetch_orders_day(today_msk)
                send_message(
                    token,
                    chat_id,
                    format_orders_message(rows, f"Заказы за {today_msk.isoformat()} (МСК)"),
                    MANAGER_KEYBOARD,
                )
                continue

            if text == "📅 Заказы за вчера":
                waiting_date.pop(chat_id, None)
                d = today_msk - timedelta(days=1)
                rows = fetch_orders_day(d)
                send_message(
                    token,
                    chat_id,
                    format_orders_message(rows, f"Заказы за {d.isoformat()} (МСК)"),
                    MANAGER_KEYBOARD,
                )
                continue

            if text == "✏️ Другая дата (ДД.ММ.ГГГГ)":
                waiting_date[chat_id] = True
                send_message(
                    token,
                    chat_id,
                    "Отправьте дату одним сообщением, например: 09.05.2026",
                    MANAGER_KEYBOARD,
                )
                continue

            m = DATE_RE.match(text)
            if m:
                dd, mm, yy = int(m.group(1)), int(m.group(2)), int(m.group(3))
                try:
                    d = date(yy, mm, dd)
                except ValueError:
                    send_message(token, chat_id, "Некорректная дата.", MANAGER_KEYBOARD)
                    continue
                waiting_date.pop(chat_id, None)
                rows = fetch_orders_day(d)
                send_message(
                    token,
                    chat_id,
                    format_orders_message(rows, f"Заказы за {d.isoformat()} (календарный день по серверу БД)"),
                    MANAGER_KEYBOARD,
                )
                continue

            if waiting_date.get(chat_id):
                send_message(
                    token,
                    chat_id,
                    "Ожидается дата в формате ДД.ММ.ГГГГ, например 09.05.2026",
                    MANAGER_KEYBOARD,
                )
                continue

            send_message(token, chat_id, "Используйте кнопки меню или /start.", MANAGER_KEYBOARD)


if __name__ == "__main__":
    main()
