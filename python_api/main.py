import base64
import hashlib
import hmac
import json
import math
import os
import secrets
import time
import urllib.error
import re
import urllib.request
from datetime import datetime, timedelta
from typing import Any, Optional

from pathlib import Path

from dotenv import load_dotenv
from fastapi import Body, FastAPI, HTTPException, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from psycopg import connect
from psycopg.rows import dict_row
from starlette.exceptions import HTTPException as StarletteHTTPException

load_dotenv(override=True)


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


DB_CONFIG = {
    "host": _env("DB_HOST", "localhost"),
    "port": int(_env("DB_PORT", "5432")),
    "dbname": _env("DB_NAME", "pc_salon"),
    "user": _env("DB_USER", "postgres"),
    "password": _env("DB_PASS", ""),
}

origins = _env("ALLOWED_ORIGINS", "*")
allow_origins = ["*"] if origins == "*" else [v.strip() for v in origins.split(",") if v.strip()]

app = FastAPI(title="PC Salon Python API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_, exc: Exception):
    # Keep PHP-compatible error payload for existing frontend handling.
    status_code = getattr(exc, "status_code", 500)
    detail = getattr(exc, "detail", "Внутренняя ошибка сервера")
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "error": str(detail)},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"success": False, "error": "Некорректные данные запроса", "details": exc.errors()},
    )


def db_conn():
    return connect(**DB_CONFIG, row_factory=dict_row)


def normalize_legacy_products() -> None:
    """
    Idempotent cleanup for legacy demo rows.
    Replaces obsolete `AURUM 4K Test` with canonical `AURUM 4K Standard`
    from the historical storefront dataset, preserving current project flow.
    """
    standard_name = "AURUM 4K Standard"
    legacy_name = "AURUM 4K Test"
    standard_payload = (
        249990.0,
        "photo/pc4_4.jpg",
        "R9 7900X",
        "RTX4070 TI",
        "Сбалансированная сборка для 4K-гейминга.",
    )

    try:
        with db_conn() as conn, conn.cursor() as cur:
            # Keep canonical image for 4K Standard synchronized with storefront assets.
            cur.execute(
                """
                UPDATE products
                SET image = %s
                WHERE category_id = %s
                  AND lower(name) = lower(%s)
                  AND COALESCE(image, '') <> %s
                """,
                (standard_payload[1], "4k", standard_name, standard_payload[1]),
            )

            # If legacy row exists and canonical row already exists, rebind all references and remove legacy.
            cur.execute(
                """
                SELECT id
                FROM products
                WHERE category_id = %s AND lower(name) = lower(%s)
                ORDER BY id ASC
                """,
                ("4k", legacy_name),
            )
            legacy_rows = cur.fetchall()

            if not legacy_rows:
                return

            cur.execute(
                """
                SELECT id
                FROM products
                WHERE category_id = %s AND lower(name) = lower(%s)
                ORDER BY id ASC
                LIMIT 1
                """,
                ("4k", standard_name),
            )
            standard_row = cur.fetchone()

            if standard_row:
                standard_id = int(standard_row["id"])
                for row in legacy_rows:
                    legacy_id = int(row["id"])
                    cur.execute(
                        """
                        UPDATE order_items
                        SET product_id = %s
                        WHERE product_id = %s
                        """,
                        (standard_id, legacy_id),
                    )
                cur.execute(
                    """
                    DELETE FROM products
                    WHERE category_id = %s AND lower(name) = lower(%s)
                    """,
                    ("4k", legacy_name),
                )
                conn.commit()
                return

            # Canonical row doesn't exist yet: repurpose the oldest legacy row.
            legacy_id = int(legacy_rows[0]["id"])
            cur.execute(
                """
                UPDATE products
                SET name = %s,
                    price = %s,
                    image = %s,
                    cpu = %s,
                    gpu = %s,
                    description = %s,
                    is_active = true
                WHERE id = %s
                """,
                (
                    standard_name,
                    standard_payload[0],
                    standard_payload[1],
                    standard_payload[2],
                    standard_payload[3],
                    standard_payload[4],
                    legacy_id,
                ),
            )

            # Remove possible duplicate legacy rows if they existed.
            cur.execute(
                """
                DELETE FROM products
                WHERE category_id = %s AND lower(name) = lower(%s) AND id <> %s
                """,
                ("4k", legacy_name, legacy_id),
            )
            conn.commit()
    except Exception as exc:
        # Cleanup should never block API startup.
        print(f"[startup] legacy products normalization skipped: {exc}")


def ensure_user_state_table() -> None:
    """Creates shared cross-device user state storage if missing."""
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS user_state (
                telegram_id bigint PRIMARY KEY,
                cart_items jsonb NOT NULL DEFAULT '[]'::jsonb,
                favorite_ids jsonb NOT NULL DEFAULT '[]'::jsonb,
                profile_finance jsonb NOT NULL DEFAULT '{}'::jsonb,
                updated_at timestamp without time zone NOT NULL DEFAULT NOW()
            )
            """
        )
        cur.execute(
            """
            ALTER TABLE user_state
            ADD COLUMN IF NOT EXISTS profile_finance jsonb NOT NULL DEFAULT '{}'::jsonb
            """
        )
        cur.execute(
            """
            ALTER TABLE user_state
            ADD COLUMN IF NOT EXISTS cart_configs jsonb NOT NULL DEFAULT '{}'::jsonb
            """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS idx_user_state_updated_at ON user_state (updated_at DESC)")
        conn.commit()


def ensure_users_is_staff_column() -> None:
    """Колонка is_staff: кто видит пункт «Панель управления» в профиле (назначается только в БД)."""
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS is_staff boolean NOT NULL DEFAULT false
            """
        )
        conn.commit()


def ensure_reviews_order_id_unique_index() -> None:
    """Не более одного отзыва на заказ (частичный уникальный индекс)."""
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS ux_reviews_order_id_not_null
            ON reviews (order_id)
            WHERE order_id IS NOT NULL
            """
        )
        conn.commit()


def ensure_products_config_json_column() -> None:
    """JSON конфигуратора (опции CPU/GPU/SSD/гарантия) для товаров из админки."""
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            ALTER TABLE products
            ADD COLUMN IF NOT EXISTS config_json jsonb NULL
            """
        )
        conn.commit()


def ensure_orders_telegram_columns() -> None:
    """Снимок Telegram при оформлении: чат с клиентом и уведомления."""
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            ALTER TABLE orders
            ADD COLUMN IF NOT EXISTS customer_telegram_id bigint NULL
            """
        )
        cur.execute(
            """
            ALTER TABLE orders
            ADD COLUMN IF NOT EXISTS telegram_username varchar(100) NULL
            """
        )
        conn.commit()


_ORDER_STATUS_RU = {
    "new": "Новый",
    "processing": "В обработке",
    "confirmed": "Подтверждён",
    "shipped": "Отправлен",
    "delivered": "Доставлен",
    "cancelled": "Отменён",
}

_PAYMENT_STATUS_RU = {
    "pending": "Ожидает оплаты",
    "paid": "Оплачен",
    "failed": "Ошибка оплаты",
}


def _money_str(value: Any) -> str:
    try:
        return f"{float(value):,.0f}".replace(",", " ")
    except (TypeError, ValueError):
        return str(value)


def _admin_chat_ids() -> list[int]:
    raw = _env("TELEGRAM_ADMIN_CHAT_IDS", "")
    if not raw:
        return []
    out: list[int] = []
    for part in raw.split(","):
        s = part.strip()
        if not s:
            continue
        try:
            out.append(int(s))
        except ValueError:
            continue
    return out


def _telegram_send_message(chat_id: int, text: str) -> None:
    token = _env("TELEGRAM_BOT_TOKEN", "")
    if not token or not text:
        return
    payload = json.dumps(
        {"chat_id": chat_id, "text": text, "disable_web_page_preview": True},
        ensure_ascii=False,
    ).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            if resp.status != 200:
                print(f"[telegram] sendMessage HTTP {resp.status}")
    except urllib.error.URLError as exc:
        print(f"[telegram] sendMessage failed: {exc}")


def _notify_admins_new_order(
    *,
    order_number: str,
    full_name: str,
    phone: str,
    total_amount: Any,
    order_status: str,
    payment_status: str,
    delivery_type: str,
    customer_telegram_id: Optional[int],
    telegram_username: Optional[str],
    items_count: int,
) -> None:
    admins = _admin_chat_ids()
    if not admins:
        return
    un = (telegram_username or "").strip().lstrip("@")
    tg_line = f"@{un}" if un else "(username скрыт)"
    if customer_telegram_id is not None:
        tg_line += f", id {customer_telegram_id}"
    dt_ru = "Доставка" if delivery_type == "delivery" else "Самовывоз"
    os_ru = _ORDER_STATUS_RU.get(order_status, order_status)
    ps_ru = _PAYMENT_STATUS_RU.get(payment_status, payment_status)
    text = (
        f"🛒 Новый заказ {order_number}\n"
        f"Клиент: {full_name}\n"
        f"Телефон: {phone}\n"
        f"Telegram: {tg_line}\n"
        f"Сумма: {_money_str(total_amount)} ₽\n"
        f"Доставка: {dt_ru}\n"
        f"Статус заказа: {os_ru}\n"
        f"Оплата: {ps_ru}\n"
        f"Позиций: {items_count}"
    )
    for cid in admins:
        _telegram_send_message(cid, text)


def _notify_customer_new_order(
    *,
    order_number: str,
    total_amount: Any,
    customer_telegram_id: Optional[int],
    delivery_type: str,
    payment_method: str,
    payment_status: str,
    is_internal_balance: bool,
) -> None:
    if customer_telegram_id is None:
        return
    try:
        chat_id = int(customer_telegram_id)
    except (TypeError, ValueError):
        return
    pm = str(payment_method or "").strip().lower()
    lines = [
        f"Спасибо! Заказ {order_number} принят.",
        f"Сумма: {_money_str(total_amount)} ₽",
    ]
    if delivery_type == "pickup":
        ready_days = 3
        hold_days = 10
        deadline = (datetime.now() + timedelta(days=hold_days)).strftime("%d.%m.%Y")
        lines.append(
            f"Самовывоз: ориентировочно через {ready_days} рабочих дня заказ будет собран и готов к выдаче."
        )
        lines.append(f"Заберите заказ до {deadline} включительно. Если не успеете — заказ будет отменён.")
        if payment_status == "paid":
            if is_internal_balance:
                lines.append(
                    "Оплата с внутреннего счёта: при отмене по истечении срока хранения сумма будет возвращена на ваш внутренний счёт в приложении (данные синхронизируются с сервером при следующем открытии)."
                )
            elif pm == "card":
                lines.append(
                    "Оплата картой: возврат средств будет оформлен на карту по регламенту банка после отмены заказа."
                )
            else:
                lines.append(
                    "При отмене по истечении срока хранения возврат оплаты согласуем с вами в переписке."
                )
        else:
            lines.append("Статусы заказа и оплаты пришлём сюда же.")
    else:
        lines.append(
            "Доставка: ориентировочно в течение 7 дней заказ будет готов к отправке."
        )
        lines.append(
            "Мы пришлём уведомление о готовности и предложим выбрать удобную дату и время доставки."
        )
        lines.append("Статусы заказа и оплаты также будем присылать сюда.")
    _telegram_send_message(chat_id, "\n".join(lines))


def _notify_customer_order_changes(prev: dict[str, Any], new: dict[str, Any]) -> None:
    raw_tid = new.get("customer_telegram_id")
    if raw_tid is None:
        return
    try:
        chat_id = int(raw_tid)
    except (TypeError, ValueError):
        return
    lines: list[str] = []
    on = new.get("order_number") or f"#{new.get('id')}"
    if prev.get("order_status") != new.get("order_status"):
        a = _ORDER_STATUS_RU.get(str(prev.get("order_status")), prev.get("order_status"))
        b = _ORDER_STATUS_RU.get(str(new.get("order_status")), new.get("order_status"))
        lines.append(f"Заказ {on}: статус «{a}» → «{b}».")
    if prev.get("payment_status") != new.get("payment_status"):
        a = _PAYMENT_STATUS_RU.get(str(prev.get("payment_status")), prev.get("payment_status"))
        b = _PAYMENT_STATUS_RU.get(str(new.get("payment_status")), new.get("payment_status"))
        lines.append(f"Заказ {on}: оплата «{a}» → «{b}».")
    if not lines:
        return
    _telegram_send_message(chat_id, "\n".join(lines))


def _normalize_telegram_username(raw: Any) -> Optional[str]:
    if raw is None:
        return None
    s = str(raw).strip().lstrip("@")
    if not s:
        return None
    return s[:100]


def json_success(data: Any, alias: Optional[str] = None, status: int = 200) -> dict[str, Any]:
    payload: dict[str, Any] = {"success": True, "data": data}
    if alias:
        payload[alias] = data
    return payload


def json_error(message: str, status: int = 400):
    raise HTTPException(status_code=status, detail=message)


ADMIN_SESSION_TTL = int(_env("ADMIN_SESSION_SECONDS", str(7 * 24 * 3600)))
MAX_SINGLE_BALANCE_INCREASE_RUB = 1_000_000.0
MAX_USER_BALANCE_RUB = 10_000_000.0

_NAME_RE = re.compile(r"^[а-яёА-ЯЁa-zA-Z\s\-']+$")
_ADDRESS_RE = re.compile(r"^[а-яёА-ЯЁa-zA-Z0-9\s\-.,№#/()'«»:;]+$")


def _admin_signing_key() -> bytes:
    secret = _env("ADMIN_TOKEN_SECRET") or _env("ADMIN_PASSWORD")
    if not secret:
        return b""
    return hashlib.sha256(f"aurum-admin|{secret}".encode()).digest()


def _parse_admin_token(token: str) -> Optional[tuple[int, str]]:
    """Возвращает (exp_ts, role) где role — 'super' или 'manager', либо None."""
    if not token or not _env("ADMIN_PASSWORD"):
        return None
    key = _admin_signing_key()
    if not key:
        return None
    try:
        padded = token + "=" * ((4 - len(token) % 4) % 4)
        raw = base64.urlsafe_b64decode(padded.encode()).decode()
        body, sig = raw.rsplit(":", 1)
        parts = body.split(".")
        if len(parts) == 2:
            exp_s, _rnd = parts
            role = "super"
        elif len(parts) == 3:
            exp_s, _rnd, rc = parts
            if rc == "S":
                role = "super"
            elif rc == "M":
                role = "manager"
            else:
                return None
        else:
            return None
        if time.time() > int(exp_s):
            return None
        expect = hmac.new(key, body.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expect):
            return None
        return (int(exp_s), role)
    except Exception:
        return None


def create_admin_token(role: str = "super") -> str:
    exp = int(time.time()) + ADMIN_SESSION_TTL
    rnd = secrets.token_hex(8)
    rc = "S" if role == "super" else "M"
    body = f"{exp}.{rnd}.{rc}"
    sig = hmac.new(_admin_signing_key(), body.encode(), hashlib.sha256).hexdigest()
    raw = f"{body}:{sig}"
    return base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")


def get_admin_role_from_request(request: Request) -> Optional[str]:
    auth = request.headers.get("authorization") or ""
    token: Optional[str] = None
    if auth.lower().startswith("bearer "):
        token = auth[7:].strip()
    if not token:
        token = request.cookies.get("aurum_admin")
    if not token:
        return None
    parsed = _parse_admin_token(token)
    return parsed[1] if parsed else None


def admin_authorized(request: Request) -> bool:
    return get_admin_role_from_request(request) is not None


def require_admin(request: Request) -> None:
    if not admin_authorized(request):
        json_error("Требуется вход в админ-панель", 401)


def require_super_admin(request: Request) -> None:
    if get_admin_role_from_request(request) != "super":
        json_error("Доступно только главному администратору", 403)


class AdminLoginPayload(BaseModel):
    password: str


class AdminStaffPayload(BaseModel):
    telegram_id: int
    is_staff: bool = True


@app.post("/api/admin/login")
def admin_login(payload: AdminLoginPayload):
    super_pw = _env("ADMIN_PASSWORD")
    mgr_pw = _env("MANAGER_ADMIN_PASSWORD", "")
    if not super_pw:
        json_error("Пароль админки не задан на сервере (переменная ADMIN_PASSWORD)", 503)
    if secrets.compare_digest(payload.password, super_pw):
        return {
            "success": True,
            "token": create_admin_token("super"),
            "role": "super",
            "expires_in": ADMIN_SESSION_TTL,
        }
    if mgr_pw and secrets.compare_digest(payload.password, mgr_pw):
        return {
            "success": True,
            "token": create_admin_token("manager"),
            "role": "manager",
            "expires_in": ADMIN_SESSION_TTL,
        }
    json_error("Неверный пароль", 401)
    return {}


@app.get("/api/admin/session")
def admin_session(request: Request):
    require_admin(request)
    role = get_admin_role_from_request(request)
    return {"success": True, "role": role}


@app.get("/api/admin/staff")
def admin_staff_list(request: Request):
    require_super_admin(request)
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, telegram_id, username, first_name, last_name, full_name, is_staff, phone
            FROM users
            WHERE is_staff = true
            ORDER BY id ASC
            """
        )
        rows = cur.fetchall()
    return json_success(rows, "staff")


@app.post("/api/admin/staff")
def admin_staff_set(request: Request, payload: AdminStaffPayload):
    require_super_admin(request)
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            UPDATE users
            SET is_staff = %s, updated_at = NOW()
            WHERE telegram_id = %s
            RETURNING id, telegram_id, is_staff
            """,
            (payload.is_staff, payload.telegram_id),
        )
        row = cur.fetchone()
        if not row:
            json_error("Пользователь с таким telegram_id не найден. Сначала откройте мини-приложение этим аккаунтом.", 404)
        conn.commit()
    return {"success": True, "data": row, "message": "Права обновлены"}


class PromoCodeCreatePayload(BaseModel):
    code: str
    discount_percent: float
    is_active: bool = True
    note: Optional[str] = None


class PromoCodePatchPayload(BaseModel):
    discount_percent: Optional[float] = None
    is_active: Optional[bool] = None
    note: Optional[str] = None


@app.get("/api/admin/promo-codes")
def admin_promo_codes_list(request: Request):
    require_admin(request)
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, code, discount_percent, is_active, note, created_at, updated_at
            FROM promo_codes
            ORDER BY id ASC
            """
        )
        rows = cur.fetchall()
    return {"success": True, "promo_codes": rows}


@app.post("/api/admin/promo-codes")
def admin_promo_codes_create(request: Request, payload: PromoCodeCreatePayload):
    require_admin(request)
    code = str(payload.code or "").strip().upper()
    if not code or len(code) > 64:
        json_error("Некорректный код", 400)
    pct = float(payload.discount_percent)
    if pct <= 0 or pct > 100:
        json_error("Процент скидки от 0.01 до 100", 400)
    note = (payload.note or "").strip() or None
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO promo_codes (code, discount_percent, is_active, note)
            VALUES (%s, %s, %s, %s)
            RETURNING id, code, discount_percent, is_active, note, created_at, updated_at
            """,
            (code, pct, bool(payload.is_active), note),
        )
        row = cur.fetchone()
        conn.commit()
    return {"success": True, "data": row}


@app.patch("/api/admin/promo-codes/{promo_id}")
def admin_promo_codes_patch(request: Request, promo_id: int, payload: PromoCodePatchPayload):
    require_admin(request)
    fields: list[str] = []
    values: list[Any] = []
    if payload.discount_percent is not None:
        p = float(payload.discount_percent)
        if p <= 0 or p > 100:
            json_error("Процент скидки от 0.01 до 100", 400)
        fields.append("discount_percent = %s")
        values.append(p)
    if payload.is_active is not None:
        fields.append("is_active = %s")
        values.append(bool(payload.is_active))
    if payload.note is not None:
        fields.append("note = %s")
        values.append((payload.note or "").strip() or None)
    if not fields:
        json_error("Нет полей для обновления", 400)
    fields.append("updated_at = NOW()")
    values.append(promo_id)
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute(
            f"UPDATE promo_codes SET {', '.join(fields)} WHERE id = %s RETURNING id, code, discount_percent, is_active, note, created_at, updated_at",
            tuple(values),
        )
        row = cur.fetchone()
        if not row:
            json_error("Промокод не найден", 404)
        conn.commit()
    return {"success": True, "data": row}


@app.delete("/api/admin/promo-codes/{promo_id}")
def admin_promo_codes_delete(request: Request, promo_id: int):
    require_admin(request)
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM promo_codes WHERE id = %s RETURNING id", (promo_id,))
        if not cur.fetchone():
            json_error("Промокод не найден", 404)
        conn.commit()
    return {"success": True}


CERTIFICATE_CODE_MAP: dict[str, float] = {
    "AURUM5": 5,
    "AURUM7": 7,
    "AURUM10": 10,
    "PREMIUM12": 12,
    "VIP15": 15,
}

MAX_DEPOSIT_HISTORY_ENTRIES = 20
MAX_BONUS_LEDGER_ENTRIES = 20


def _certificate_discount_percent(cur: Any, code: str) -> Optional[float]:
    """Активный промокод в БД (таблица promo_codes), иначе встроенный CERTIFICATE_CODE_MAP."""
    c = str(code or "").strip().upper()
    if not c:
        return None
    cur.execute(
        "SELECT discount_percent FROM promo_codes WHERE code = %s AND is_active = TRUE",
        (c,),
    )
    row = cur.fetchone()
    if row is not None:
        return float(row["discount_percent"])
    v = CERTIFICATE_CODE_MAP.get(c)
    return float(v) if v is not None else None


def normalize_phone_digits(phone: Optional[str]) -> str:
    return "".join(c for c in (phone or "") if c.isdigit())


def _normalize_ru_phone_11_digits(phone: Optional[str]) -> Optional[str]:
    d = normalize_phone_digits(phone)
    if len(d) == 11 and d[0] == "8":
        d = "7" + d[1:]
    if len(d) == 10:
        d = "7" + d
    if len(d) != 11 or d[0] != "7":
        return None
    if not re.match(r"^7[3-9]\d{9}$", d):
        return None
    return d


def _format_ru_phone_display(d11: str) -> str:
    return f"+7({d11[1:4]}){d11[4:7]}-{d11[7:9]}-{d11[9:11]}"


def _title_name_token(token: str) -> str:
    """Первая буква слова — заглавная, остальные строчные; поддержка дефисов (Анна-Мария)."""
    parts = token.split("-")
    out: list[str] = []
    for p in parts:
        if not p:
            continue
        out.append(p[0].upper() + p[1:].lower() if len(p) > 1 else p.upper())
    return "-".join(out)


def _validate_order_full_name(raw: str) -> str:
    s = (raw or "").strip()
    s = re.sub(r"\s+", " ", s)
    words = [w for w in s.split(" ") if w]
    if len(words) < 2 or len(words) > 3:
        json_error("ФИО: укажите от 2 до 3 слов (фамилия, имя и при необходимости отчество)", 400)
    titled: list[str] = []
    for w in words:
        if not re.match(r"^[а-яёА-ЯЁa-zA-Z]+(?:['-][а-яёА-ЯЁa-zA-Z]+)*$", w):
            json_error("ФИО: в каждом слове допустимы только буквы, дефис и апостроф", 400)
        titled.append(_title_name_token(w))
    out = " ".join(titled)
    if len(out) > 100:
        json_error("ФИО не длиннее 100 символов", 400)
    if not re.search(r"[а-яёА-ЯЁa-zA-Z]", out):
        json_error("ФИО должно содержать буквы", 400)
    return out


def _validate_order_address(raw: Any) -> str:
    s = str(raw or "").strip()
    if len(s) < 10 or len(s) > 500:
        json_error("Адрес доставки: от 10 до 500 символов", 400)
    if not _ADDRESS_RE.match(s):
        json_error("Адрес содержит недопустимые символы", 400)
    return s


def _validate_order_comment(raw: Any) -> Optional[str]:
    if raw is None or str(raw).strip() == "":
        return None
    s = str(raw).strip()
    if len(s) > 500:
        json_error("Комментарий к заказу не длиннее 500 символов", 400)
    return s


class UserUpsertPayload(BaseModel):
    telegram_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    address: Optional[str] = None


class ProductCreatePayload(BaseModel):
    category_id: str
    name: str
    price: float
    image: Optional[str] = None
    cpu: Optional[str] = None
    gpu: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = True


class ReviewCreatePayload(BaseModel):
    user_id: int
    rating: int
    order_id: Optional[int] = None
    product_id: Optional[int] = None
    title: Optional[str] = None
    comment: Optional[str] = None


class ReviewPublishPayload(BaseModel):
    is_published: bool


def _enrich_reviews_order_items(reviews: list[dict[str, Any]]) -> None:
    if not reviews:
        return
    oids_set: set[int] = set()
    for r in reviews:
        oid = r.get("order_id")
        if oid is not None:
            try:
                oids_set.add(int(oid))
            except (TypeError, ValueError):
                pass
    if not oids_set:
        for r in reviews:
            r["order_items"] = []
        return
    oids = sorted(oids_set)
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT order_id, item_name, quantity, item_specs, item_type
            FROM order_items
            WHERE order_id = ANY(%s)
            ORDER BY order_id ASC, id ASC
            """,
            (oids,),
        )
        rows = cur.fetchall()
    by_oid: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        oid = int(row["order_id"])
        by_oid.setdefault(oid, []).append(
            {
                "item_name": row.get("item_name"),
                "quantity": row.get("quantity"),
                "item_specs": row.get("item_specs"),
                "item_type": row.get("item_type"),
            }
        )
    for r in reviews:
        oid = r.get("order_id")
        if oid is None:
            r["order_items"] = []
            continue
        try:
            io = int(oid)
        except (TypeError, ValueError):
            r["order_items"] = []
            continue
        r["order_items"] = by_oid.get(io, [])


@app.get("/api/health")
@app.get("/health")
def health() -> dict[str, Any]:
    return {"ok": True}


@app.get("/api/categories")
def categories_get():
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, name, image, display_order AS "displayOrder"
            FROM categories
            ORDER BY display_order ASC
            """
        )
        categories = cur.fetchall()
    return json_success(categories, "categories")


@app.get("/api/products")
def products_get(
    request: Request,
    category: Optional[str] = Query(default=None),
    id: Optional[int] = Query(default=None),
    admin: Optional[str] = Query(default=None),
    admin_mode: Optional[str] = Query(default=None),
):
    with db_conn() as conn, conn.cursor() as cur:
        if id is not None:
            cur.execute(
                """
                SELECT id, name, price, image, cpu, gpu, description, category_id, config_json
                FROM products
                WHERE id = %s AND is_active = true
                """,
                (id,),
            )
            product = cur.fetchone()
            if not product:
                json_error("Товар не найден", 404)
            return {"success": True, "data": product, "product": product}

        if category is not None:
            cur.execute(
                """
                SELECT id, name, price, image, cpu, gpu, description, category_id, config_json
                FROM products
                WHERE category_id = %s AND is_active = true
                ORDER BY id ASC
                """,
                (category,),
            )
            products = cur.fetchall()
            return json_success(products, "products")

        show_all = ((admin == "1") or (admin_mode == "true")) and admin_authorized(request)
        if show_all:
            cur.execute(
                """
                SELECT id, name, price, image, cpu, gpu, category_id, description, is_active, config_json
                FROM products
                ORDER BY category_id, id
                """
            )
        else:
            cur.execute(
                """
                SELECT id, name, price, image, cpu, gpu, category_id, description, is_active, config_json
                FROM products
                WHERE is_active = true
                ORDER BY category_id, id
                """
            )
        products = cur.fetchall()
        return json_success(products, "products")


def _coerce_bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    if v in (0, 1, "0", "1"):
        return bool(int(v))
    return bool(v)


def _parse_config_json_payload(raw: Any) -> Optional[dict[str, Any]]:
    if raw is None:
        return None
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str) and raw.strip():
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return None
        return parsed if isinstance(parsed, dict) else None
    return None


def _products_admin_update(product_id: int, data: dict[str, Any]) -> dict[str, Any]:
    fields: list[str] = []
    values: list[Any] = []
    price_int_for_config_sync: int | None = None
    if "category_id" in data:
        fields.append("category_id = %s")
        values.append(data["category_id"])
    if "name" in data:
        fields.append("name = %s")
        values.append(data["name"])
    if "price" in data:
        try:
            pv = float(data["price"])
        except (TypeError, ValueError):
            json_error("Некорректная цена", 400)
        if pv < 0 or math.isnan(pv) or math.isinf(pv):
            json_error("Некорректная цена", 400)
        price_int_for_config_sync = int(round(pv))
        fields.append("price = %s")
        values.append(price_int_for_config_sync)
    if "image" in data:
        fields.append("image = %s")
        values.append(data["image"])
    if "cpu" in data:
        fields.append("cpu = %s")
        values.append(data["cpu"])
    if "gpu" in data:
        fields.append("gpu = %s")
        values.append(data["gpu"])
    if "description" in data:
        fields.append("description = %s")
        values.append(data["description"])
    if "is_active" in data:
        fields.append("is_active = %s")
        values.append(_coerce_bool(data["is_active"]))
    if "config_json" in data:
        raw_cfg = data.get("config_json")
        if raw_cfg is None:
            fields.append("config_json = NULL")
        else:
            cfg = _parse_config_json_payload(raw_cfg)
            if cfg is None:
                json_error("Некорректный config_json", 400)
            fields.append("config_json = CAST(%s AS jsonb)")
            values.append(json.dumps(cfg, ensure_ascii=False))
    if not fields:
        json_error("Нет полей для обновления", 400)
    values.append(product_id)
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id FROM products WHERE id = %s", (product_id,))
        if not cur.fetchone():
            json_error("Товар не найден", 404)
        cur.execute("UPDATE products SET " + ", ".join(fields) + " WHERE id = %s", values)
        if price_int_for_config_sync is not None and "config_json" not in data:
            cur.execute(
                """
                UPDATE products
                SET config_json = jsonb_set(config_json, '{basePrice}', to_jsonb(%s::int), true)
                WHERE id = %s AND config_json IS NOT NULL
                """,
                (price_int_for_config_sync, product_id),
            )
        cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        product = cur.fetchone()
        conn.commit()
    return jsonable_encoder({"success": True, "data": product, "message": "Товар успешно обновлен"})


def _products_admin_create(data: dict[str, Any]) -> JSONResponse:
    category_id = data.get("category_id")
    name = (data.get("name") or "").strip() if data.get("name") is not None else ""
    price = data.get("price")
    if not category_id or not name or price is None or price == "":
        json_error("Обязательные поля: category_id, name, price", 400)
    try:
        price_val = float(price)
    except (TypeError, ValueError):
        json_error("Некорректная цена", 400)
    if price_val < 0 or math.isnan(price_val) or math.isinf(price_val):
        json_error("Некорректная цена", 400)
    price_val = round(price_val)
    cfg = _parse_config_json_payload(data.get("config_json"))
    cfg_sql: Optional[str] = json.dumps(cfg, ensure_ascii=False) if cfg is not None else None
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id FROM categories WHERE id = %s", (category_id,))
        if not cur.fetchone():
            json_error("Категория не найдена", 400)
        cur.execute(
            """
            INSERT INTO products (category_id, name, price, image, cpu, gpu, description, is_active, config_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CAST(%s AS jsonb))
            RETURNING id
            """,
            (
                category_id,
                name,
                price_val,
                data.get("image"),
                data.get("cpu"),
                data.get("gpu"),
                data.get("description"),
                _coerce_bool(data.get("is_active", True)),
                cfg_sql,
            ),
        )
        new_id = cur.fetchone()["id"]
        cur.execute("SELECT * FROM products WHERE id = %s", (new_id,))
        product = cur.fetchone()
        conn.commit()
    # JSONResponse без jsonable_encoder ломается на Decimal/datetime из PostgreSQL → 500
    return JSONResponse(
        status_code=201,
        content=jsonable_encoder(
            {"success": True, "data": product, "message": "Товар успешно создан"}
        ),
    )


@app.post("/api/products")
def products_post(
    request: Request,
    payload: dict[str, Any] = Body(...),
    id: Optional[int] = Query(default=None),
    action: Optional[str] = Query(default=None),
):
    require_admin(request)
    if action == "update" and id is not None:
        return _products_admin_update(id, payload)
    res = _products_admin_create(payload)
    return res


@app.delete("/api/products")
def products_delete(request: Request, id: int = Query(..., description="ID товара")):
    require_admin(request)
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM products WHERE id = %s RETURNING id", (id,))
        if not cur.fetchone():
            json_error("Товар не найден", 404)
        conn.commit()
    return {"success": True, "message": "Товар успешно удален из базы данных"}


@app.get("/api/reviews")
def reviews_get(
    request: Request,
    user_id: Optional[int] = Query(default=None),
    telegram_id: Optional[int] = Query(default=None),
    product_id: Optional[int] = Query(default=None),
    order_id: Optional[int] = Query(default=None),
    published: Optional[str] = Query(default=None),
    admin: Optional[str] = Query(default=None),
):
    where: list[str] = []
    params: list[Any] = []
    if admin == "1":
        require_admin(request)
    elif telegram_id is not None and user_id is None:
        with db_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE telegram_id = %s", (telegram_id,))
            row = cur.fetchone()
        if not row:
            return json_success([], "reviews")
        user_id = int(row["id"])
    if admin != "1" and user_id is not None:
        where.append("r.user_id = %s")
        params.append(user_id)
    if product_id is not None:
        where.append("r.product_id = %s")
        params.append(product_id)
    if order_id is not None:
        where.append("r.order_id = %s")
        params.append(order_id)
    if published is not None:
        where.append("r.is_published = %s")
        params.append(published == "true")

    if admin != "1" and not where:
        json_error(
            "Укажите параметр: telegram_id, user_id, product_id, order_id или published",
            400,
        )

    sql = """
        SELECT
            r.id,
            r.user_id,
            r.order_id,
            r.product_id,
            r.rating,
            r.title,
            r.comment,
            r.is_published,
            r.created_at,
            r.updated_at,
            u.first_name,
            u.last_name,
            u.username,
            p.name AS product_name
        FROM reviews r
        LEFT JOIN users u ON r.user_id = u.id
        LEFT JOIN products p ON r.product_id = p.id
    """
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY r.created_at DESC"

    with db_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        reviews = cur.fetchall()
    _enrich_reviews_order_items(reviews)
    return json_success(reviews, "reviews")


@app.post("/api/reviews")
def reviews_post(payload: ReviewCreatePayload):
    if payload.rating < 1 or payload.rating > 5:
        json_error("Рейтинг должен быть от 1 до 5", 400)

    with db_conn() as conn, conn.cursor() as cur:
        if payload.order_id is not None:
            cur.execute("SELECT 1 FROM reviews WHERE order_id = %s LIMIT 1", (payload.order_id,))
            if cur.fetchone():
                json_error("По этому заказу отзыв уже оставлен", 409)

        cur.execute(
            """
            INSERT INTO reviews (user_id, order_id, product_id, rating, title, comment, is_published)
            VALUES (%s, %s, %s, %s, %s, %s, false)
            RETURNING id
            """,
            (
                payload.user_id,
                payload.order_id,
                payload.product_id,
                payload.rating,
                payload.title,
                payload.comment,
            ),
        )
        review_id = cur.fetchone()["id"]
        cur.execute(
            """
            SELECT
                r.*,
                u.first_name,
                u.last_name,
                p.name AS product_name
            FROM reviews r
            LEFT JOIN users u ON r.user_id = u.id
            LEFT JOIN products p ON r.product_id = p.id
            WHERE r.id = %s
            """,
            (review_id,),
        )
        review = cur.fetchone()
        conn.commit()
    return {"success": True, "data": review, "message": "Отзыв успешно создан"}


@app.patch("/api/reviews/{review_id}")
def reviews_patch(review_id: int, request: Request, payload: ReviewPublishPayload):
    require_admin(request)
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            UPDATE reviews
            SET is_published = %s, updated_at = NOW()
            WHERE id = %s
            RETURNING id, is_published, updated_at
            """,
            (payload.is_published, review_id),
        )
        row = cur.fetchone()
        if not row:
            json_error("Отзыв не найден", 404)
        conn.commit()
    return {"success": True, "data": dict(row), "message": "Статус отзыва обновлён"}


@app.get("/api/users")
def users_get(
    telegram_id: Optional[int] = Query(default=None),
    phone: Optional[str] = Query(default=None),
):
    with db_conn() as conn, conn.cursor() as cur:
        if telegram_id is not None:
            cur.execute(
                """
                SELECT id, telegram_id, first_name, last_name, username, phone, full_name, address, is_staff, created_at, updated_at
                FROM users
                WHERE telegram_id = %s
                """,
                (telegram_id,),
            )
            user = cur.fetchone()
            return {"success": True, "user": user}
        digits = normalize_phone_digits(phone)
        if digits:
            cur.execute(
                """
                SELECT id, telegram_id, first_name, last_name, username, phone, full_name, address, is_staff, created_at, updated_at
                FROM users
                WHERE regexp_replace(coalesce(phone, ''), '[^0-9]', '', 'g') = %s
                LIMIT 1
                """,
                (digits,),
            )
            user = cur.fetchone()
            return {"success": True, "user": user}
    json_error("Укажите telegram_id или phone", 400)


@app.post("/api/users")
def users_post(payload: UserUpsertPayload):
    if not payload.telegram_id and not payload.phone:
        json_error("telegram_id или phone обязателен", 400)

    with db_conn() as conn, conn.cursor() as cur:
        if payload.telegram_id:
            cur.execute("SELECT id FROM users WHERE telegram_id = %s", (payload.telegram_id,))
            exists = cur.fetchone()
        else:
            cur.execute("SELECT id FROM users WHERE phone = %s", (payload.phone,))
            exists = cur.fetchone()

        if exists:
            user_id = exists["id"]
            cur.execute(
                """
                UPDATE users SET
                    telegram_id = COALESCE(%s, telegram_id),
                    first_name = COALESCE(%s, first_name),
                    last_name = COALESCE(%s, last_name),
                    username = COALESCE(%s, username),
                    phone = COALESCE(%s, phone),
                    full_name = COALESCE(%s, full_name),
                    address = COALESCE(%s, address)
                WHERE id = %s
                """,
                (
                    payload.telegram_id,
                    payload.first_name,
                    payload.last_name,
                    payload.username,
                    payload.phone,
                    payload.full_name,
                    payload.address,
                    user_id,
                ),
            )
        else:
            cur.execute(
                """
                INSERT INTO users (telegram_id, first_name, last_name, username, phone, full_name, address)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    payload.telegram_id,
                    payload.first_name,
                    payload.last_name,
                    payload.username,
                    payload.phone,
                    payload.full_name,
                    payload.address,
                ),
            )
            user_id = cur.fetchone()["id"]

        cur.execute(
            """
            SELECT id, telegram_id, first_name, last_name, username, phone, full_name, address, is_staff, created_at, updated_at
            FROM users
            WHERE id = %s
            """,
            (user_id,),
        )
        user = cur.fetchone()
        conn.commit()
    return {"success": True, "user": user, "message": "Пользователь сохранён"}


def _normalize_cart_items(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    normalized: list[dict[str, Any]] = []
    for row in value:
        if not isinstance(row, dict):
            continue
        raw_id = row.get("id")
        if raw_id is None:
            continue
        qty_raw = row.get("qty", 1)
        try:
            qty = int(qty_raw)
        except (TypeError, ValueError):
            qty = 1
        if qty < 1:
            qty = 1
        normalized.append({"id": str(raw_id), "qty": qty})
    return normalized


def _normalize_cart_configs(value: Any) -> dict[str, Any]:
    """Снимки config_* для строк корзины вида config-<productId>-<ts> (синхронизация между устройствами)."""
    if not isinstance(value, dict):
        return {}
    out: dict[str, Any] = {}
    for raw_k, raw_v in list(value.items())[:60]:
        k = str(raw_k).strip()
        if not k or len(k) > 220:
            continue
        if not isinstance(raw_v, dict):
            continue
        out[k] = raw_v
    return out


def _normalize_favorite_ids(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(v) for v in value if v is not None]


def _normalize_deposit_history_entries(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    out: list[dict[str, Any]] = []
    for e in value[:80]:
        if not isinstance(e, dict):
            continue
        eid = str(e.get("id") or "").strip()
        if not eid:
            continue
        try:
            amount = float(e.get("amount", 0))
        except (TypeError, ValueError):
            amount = 0.0
        try:
            balance_after = float(e.get("balance_after", 0))
        except (TypeError, ValueError):
            balance_after = 0.0
        created = e.get("created_at")
        created_at = (
            created.isoformat()
            if hasattr(created, "isoformat")
            else (str(created).strip() if created is not None else datetime.utcnow().isoformat() + "Z")
        )
        if amount <= 0:
            continue
        out.append(
            {
                "id": eid,
                "amount": round(max(0.0, amount), 2),
                "balance_after": round(max(0.0, balance_after), 2),
                "created_at": created_at,
            }
        )
    return out[:MAX_DEPOSIT_HISTORY_ENTRIES]


def _merge_deposit_history_lists(a: list[dict[str, Any]], b: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for lst in (a, b):
        for e in lst:
            eid = str(e.get("id") or "").strip()
            if not eid:
                continue
            by_id[eid] = e
    merged = list(by_id.values())
    merged.sort(key=lambda x: str(x.get("created_at") or ""), reverse=True)
    return merged[:MAX_DEPOSIT_HISTORY_ENTRIES]


def _deposit_history_revision_int(value: Any) -> int:
    try:
        r = int(value)
        return max(0, r)
    except (TypeError, ValueError):
        return 0


def _normalize_profile_finance(value: Any) -> dict[str, Any]:
    src = value if isinstance(value, dict) else {}
    balance_raw = src.get("balance", 0)
    bonuses_raw = src.get("bonuses", 0)
    discount_raw = src.get("personalDiscount", 0)
    try:
        balance = float(balance_raw)
    except (TypeError, ValueError):
        balance = 0.0
    try:
        bonuses = float(bonuses_raw)
    except (TypeError, ValueError):
        bonuses = 0.0
    try:
        personal_discount = float(discount_raw)
    except (TypeError, ValueError):
        personal_discount = 0.0
    active_code = src.get("activeCertificateCode")
    active_code_norm = None if active_code is None else str(active_code).strip().upper() or None
    deposits = _normalize_deposit_history_entries(src.get("deposit_history"))
    dep_rev = _deposit_history_revision_int(src.get("deposit_history_revision"))
    return {
        "balance": max(0.0, balance),
        "bonuses": max(0.0, bonuses),
        "personalDiscount": max(0.0, personal_discount),
        "activeCertificateCode": active_code_norm,
        "deposit_history": deposits,
        "deposit_history_revision": dep_rev,
    }


def _normalize_profile_finance_core(value: Any) -> dict[str, Any]:
    """Только баланс/бонусы/скидка/сертификат — для слияния с deposit_history на запись."""
    src = value if isinstance(value, dict) else {}
    full = _normalize_profile_finance(src)
    return {k: full[k] for k in ("balance", "bonuses", "personalDiscount", "activeCertificateCode")}


@app.get("/api/user-state")
def user_state_get(telegram_id: int = Query(...)):
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT telegram_id, cart_items, favorite_ids, profile_finance, cart_configs, updated_at
            FROM user_state
            WHERE telegram_id = %s
            """,
            (telegram_id,),
        )
        row = cur.fetchone()
    if not row:
        payload = {
            "telegram_id": telegram_id,
            "cart_items": [],
            "favorite_ids": [],
            "profile_finance": _normalize_profile_finance({}),
            "cart_configs": {},
            "updated_at": None,
        }
    else:
        cc_raw = row.get("cart_configs")
        payload = {
            "telegram_id": int(row["telegram_id"]),
            "cart_items": _normalize_cart_items(row.get("cart_items")),
            "favorite_ids": _normalize_favorite_ids(row.get("favorite_ids")),
            "profile_finance": _normalize_profile_finance(row.get("profile_finance")),
            "cart_configs": _normalize_cart_configs(cc_raw) if isinstance(cc_raw, dict) else {},
            "updated_at": row.get("updated_at"),
        }
    return {"success": True, "data": payload, "state": payload}


@app.post("/api/user-state")
def user_state_post(payload: dict[str, Any] = Body(...)):
    raw_tid = payload.get("telegram_id")
    if raw_tid is None:
        json_error("telegram_id обязателен", 400)
    try:
        tid = int(raw_tid)
    except (TypeError, ValueError):
        json_error("Некорректный telegram_id", 400)

    cart_items = _normalize_cart_items(payload.get("cart_items"))
    favorite_ids = _normalize_favorite_ids(payload.get("favorite_ids"))
    incoming_pf = payload.get("profile_finance")
    incoming_pf_dict = incoming_pf if isinstance(incoming_pf, dict) else {}
    core = _normalize_profile_finance_core(incoming_pf_dict)
    incoming_dep = _normalize_deposit_history_entries(incoming_pf_dict.get("deposit_history"))
    incoming_dep_rev = _deposit_history_revision_int(incoming_pf_dict.get("deposit_history_revision"))

    with db_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT profile_finance, cart_configs FROM user_state WHERE telegram_id = %s
            """,
            (tid,),
        )
        prev_row = cur.fetchone()
        existing_raw = prev_row.get("profile_finance") if prev_row else None
        existing_pf = existing_raw if isinstance(existing_raw, dict) else {}
        existing_full = _normalize_profile_finance(existing_pf)
        server_dep_rev = int(existing_full["deposit_history_revision"])
        existing_dep = list(existing_full["deposit_history"])
        if incoming_dep_rev < server_dep_rev:
            merged_dep = existing_dep
        else:
            merged_dep = _merge_deposit_history_lists(existing_dep, incoming_dep)
        prev_bal = float(_normalize_profile_finance(existing_pf)["balance"])
        new_bal = float(core["balance"])
        if new_bal > prev_bal + MAX_SINGLE_BALANCE_INCREASE_RUB + 1e-6:
            json_error(
                f"За одно пополнение баланс можно увеличить не более чем на {int(MAX_SINGLE_BALANCE_INCREASE_RUB):,} ₽".replace(
                    ",", " "
                ),
                400,
            )
        if new_bal > MAX_USER_BALANCE_RUB + 1e-6:
            json_error(
                f"Баланс не может превышать {int(MAX_USER_BALANCE_RUB):,} ₽".replace(",", " "),
                400,
            )
        profile_finance = {**core, "deposit_history": merged_dep, "deposit_history_revision": server_dep_rev}

        if "cart_configs" in payload:
            cart_configs = _normalize_cart_configs(payload.get("cart_configs"))
        else:
            cc_prev = prev_row.get("cart_configs") if prev_row else None
            cart_configs = _normalize_cart_configs(cc_prev) if isinstance(cc_prev, dict) else {}

        cur.execute(
            """
            INSERT INTO user_state (telegram_id, cart_items, favorite_ids, profile_finance, cart_configs, updated_at)
            VALUES (%s, %s::jsonb, %s::jsonb, %s::jsonb, %s::jsonb, NOW())
            ON CONFLICT (telegram_id) DO UPDATE SET
                cart_items = EXCLUDED.cart_items,
                favorite_ids = EXCLUDED.favorite_ids,
                profile_finance = EXCLUDED.profile_finance,
                cart_configs = EXCLUDED.cart_configs,
                updated_at = NOW()
            RETURNING telegram_id, cart_items, favorite_ids, profile_finance, cart_configs, updated_at
            """,
            (
                tid,
                json.dumps(cart_items, ensure_ascii=False),
                json.dumps(favorite_ids, ensure_ascii=False),
                json.dumps(profile_finance, ensure_ascii=False),
                json.dumps(cart_configs, ensure_ascii=False),
            ),
        )
        row = cur.fetchone()
        conn.commit()

    cc_out = row.get("cart_configs")
    state = {
        "telegram_id": int(row["telegram_id"]),
        "cart_items": _normalize_cart_items(row.get("cart_items")),
        "favorite_ids": _normalize_favorite_ids(row.get("favorite_ids")),
        "profile_finance": _normalize_profile_finance(row.get("profile_finance")),
        "cart_configs": _normalize_cart_configs(cc_out) if isinstance(cc_out, dict) else {},
        "updated_at": row.get("updated_at"),
    }
    return {"success": True, "data": state, "state": state, "message": "Состояние пользователя сохранено"}


@app.get("/api/certificates")
def certificates_get(telegram_id: int = Query(..., description="Telegram user id")):
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT code FROM certificate_redemptions
            WHERE telegram_id = %s
            ORDER BY redeemed_at DESC
            """,
            (telegram_id,),
        )
        used_codes = [row["code"] for row in cur.fetchall()]
        cur.execute(
            """
            SELECT code, discount_percent, updated_at
            FROM certificate_pending
            WHERE telegram_id = %s
            """,
            (telegram_id,),
        )
        pending = cur.fetchone()
    return {"success": True, "used_codes": used_codes, "pending": pending}


@app.post("/api/certificates")
def certificates_activate(payload: dict[str, Any] = Body(...)):
    raw_tid = payload.get("telegram_id")
    code = str(payload.get("code") or "").strip().upper()
    if raw_tid is None or not code:
        json_error("telegram_id и code обязательны", 400)
    try:
        tid = int(raw_tid)
    except (TypeError, ValueError):
        json_error("Некорректный telegram_id", 400)
    with db_conn() as conn, conn.cursor() as cur:
        pct = _certificate_discount_percent(cur, code)
        if pct is None:
            json_error("Код сертификата не найден или недействителен", 400)
        cur.execute(
            "SELECT 1 FROM certificate_redemptions WHERE telegram_id = %s AND code = %s",
            (tid, code),
        )
        if cur.fetchone():
            json_error("Этот сертификат уже был использован", 400)
        cur.execute(
            """
            INSERT INTO certificate_pending (telegram_id, code, discount_percent)
            VALUES (%s, %s, %s)
            ON CONFLICT (telegram_id) DO UPDATE SET
                code = EXCLUDED.code,
                discount_percent = EXCLUDED.discount_percent,
                updated_at = NOW()
            """,
            (tid, code, float(pct)),
        )
        conn.commit()
    return {
        "success": True,
        "code": code,
        "discount_percent": float(pct),
        "message": "Сертификат активирован",
    }


@app.get("/api/bonus-ledger")
def bonus_ledger_get(telegram_id: int = Query(...)):
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, telegram_id, user_id, order_id, order_number, entry_type, amount, note, created_at
            FROM bonus_ledger
            WHERE telegram_id = %s
            ORDER BY created_at DESC, id DESC
            LIMIT %s
            """,
            (telegram_id, MAX_BONUS_LEDGER_ENTRIES),
        )
        rows = cur.fetchall()
    return json_success(rows, "entries")


@app.get("/api/orders")
def orders_get(
    request: Request,
    user_id: Optional[int] = Query(default=None),
    telegram_id: Optional[int] = Query(default=None),
    phone: Optional[str] = Query(default=None),
    id: Optional[int] = Query(default=None),
    admin: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
):
    with db_conn() as conn, conn.cursor() as cur:
        if admin == "1" and id is None and user_id is None and telegram_id is None and phone is None:
            require_admin(request)
            sql = """
                SELECT o.*, u.phone as user_phone, u.full_name as user_name, u.username as user_username
                FROM orders o
                LEFT JOIN users u ON o.user_id = u.id
            """
            params: list[Any] = []
            if status:
                sql += " WHERE o.order_status = %s"
                params.append(status)
            sql += " ORDER BY o.created_at DESC"
            cur.execute(sql, params)
            orders = cur.fetchall()
            for order in orders:
                cur.execute("SELECT * FROM order_items WHERE order_id = %s", (order["id"],))
                order["items"] = cur.fetchall()
            return {"success": True, "data": orders, "orders": orders}

        if id is not None:
            require_admin(request)
            cur.execute("SELECT * FROM orders WHERE id = %s", (id,))
            order = cur.fetchone()
            if not order:
                json_error("Заказ не найден", 404)
            cur.execute("SELECT * FROM order_items WHERE order_id = %s", (id,))
            order["items"] = cur.fetchall()
            return {"success": True, "data": order, "order": order}

        if telegram_id is not None:
            cur.execute("SELECT id, phone FROM users WHERE telegram_id = %s", (telegram_id,))
            user = cur.fetchone()
            if not user:
                return {"success": True, "data": [], "orders": []}

            cur.execute("SELECT * FROM orders WHERE user_id = %s ORDER BY created_at DESC", (user["id"],))
            orders_by_user = cur.fetchall()

            if user["phone"]:
                cur.execute(
                    "SELECT * FROM orders WHERE user_id IS NULL AND phone = %s ORDER BY created_at DESC",
                    (user["phone"],),
                )
                orders_by_phone = cur.fetchall()
            else:
                orders_by_phone = []

            seen = {o["id"] for o in orders_by_user}
            orders = orders_by_user + [o for o in orders_by_phone if o["id"] not in seen]
            for order in orders:
                cur.execute("SELECT * FROM order_items WHERE order_id = %s", (order["id"],))
                order["items"] = cur.fetchall()
            return {"success": True, "data": orders, "orders": orders}

        if phone is not None:
            digits = normalize_phone_digits(phone)
            if not digits:
                return {"success": True, "data": [], "orders": []}
            cur.execute(
                """
                SELECT * FROM orders
                WHERE regexp_replace(coalesce(phone, ''), '[^0-9]', '', 'g') = %s
                ORDER BY created_at DESC
                """,
                (digits,),
            )
            by_phone_col = cur.fetchall()
            cur.execute(
                """
                SELECT o.* FROM orders o
                INNER JOIN users u ON u.id = o.user_id
                WHERE regexp_replace(coalesce(u.phone, ''), '[^0-9]', '', 'g') = %s
                ORDER BY o.created_at DESC
                """,
                (digits,),
            )
            by_user = cur.fetchall()
            seen: set[Any] = set()
            merged: list[dict[str, Any]] = []
            for o in by_phone_col + by_user:
                oid = o["id"]
                if oid in seen:
                    continue
                seen.add(oid)
                merged.append(o)
            merged.sort(key=lambda x: x["created_at"], reverse=True)
            for order in merged:
                cur.execute("SELECT * FROM order_items WHERE order_id = %s", (order["id"],))
                order["items"] = cur.fetchall()
            return {"success": True, "data": merged, "orders": merged}

        if user_id is not None:
            cur.execute("SELECT * FROM orders WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
            orders = cur.fetchall()
            for order in orders:
                cur.execute("SELECT * FROM order_items WHERE order_id = %s", (order["id"],))
                order["items"] = cur.fetchall()
            return {"success": True, "data": orders, "orders": orders}

    json_error("Необходим параметр user_id, telegram_id, phone, id или admin=1", 400)
    return {}


def _orders_admin_update(order_id: int, data: dict[str, Any]) -> dict[str, Any]:
    allowed_order = {"new", "processing", "confirmed", "shipped", "delivered", "cancelled"}
    allowed_pay = {"pending", "paid", "failed"}
    fields: list[str] = []
    values: list[Any] = []
    if "order_status" in data and data["order_status"] in allowed_order:
        fields.append("order_status = %s")
        values.append(data["order_status"])
    if "payment_status" in data and data["payment_status"] in allowed_pay:
        fields.append("payment_status = %s")
        values.append(data["payment_status"])
    if "comment" in data:
        fields.append("comment = %s")
        values.append(data["comment"])
    if not fields:
        json_error("Нет полей для обновления", 400)
    values.append(order_id)
    prev_snapshot: Optional[dict[str, Any]] = None
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
        prev_row = cur.fetchone()
        if not prev_row:
            json_error("Заказ не найден", 404)
        prev_snapshot = dict(prev_row)
        cur.execute("UPDATE orders SET " + ", ".join(fields) + " WHERE id = %s", values)
        cur.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
        order = cur.fetchone()
        cur.execute("SELECT * FROM order_items WHERE order_id = %s", (order_id,))
        order["items"] = cur.fetchall()
        conn.commit()
    if prev_snapshot and order:
        _notify_customer_order_changes(prev_snapshot, dict(order))
    return {"success": True, "data": order, "order": order, "message": "Заказ успешно обновлен"}


def _orders_create(payload: dict[str, Any]) -> dict[str, Any]:
    items = payload.get("items", [])
    full_name = (payload.get("full_name") or "").strip()
    phone = (payload.get("phone") or "").strip()
    total_amount = float(payload.get("total_amount") or 0)
    delivery_type = payload.get("delivery_type") or "pickup"
    address = payload.get("address")
    comment = payload.get("comment")
    payment_method = payload.get("payment_method") or "cash"
    user_id = payload.get("user_id")

    raw_tid = payload.get("telegram_id")
    tid: Optional[int] = None
    if raw_tid is not None and str(raw_tid).strip() != "":
        try:
            tid = int(raw_tid)
        except (TypeError, ValueError):
            tid = None

    cert_code = str(payload.get("certificate_code") or "").strip().upper()
    discount_amount = float(payload.get("discount_amount") or 0)
    bonus_used = int(payload.get("bonus_used") or 0)
    bonus_earned = int(payload.get("bonus_earned") or 0)

    if not items or not full_name or not phone or total_amount <= 0:
        json_error("Обязательные поля не заполнены", 400)

    full_name = _validate_order_full_name(full_name)
    d11 = _normalize_ru_phone_11_digits(phone)
    if not d11:
        json_error("Некорректный номер телефона (нужен российский номер: 10–11 цифр, код +7 или 8).", 400)
    phone = _format_ru_phone_display(d11)

    if delivery_type == "delivery" and not (address and str(address).strip()):
        json_error("Адрес доставки обязателен для заказа с доставкой", 400)

    telegram_username = _normalize_telegram_username(payload.get("telegram_username"))

    payment_method_ui = str(payload.get("payment_method_ui") or "").strip().lower()
    pm = str(payment_method or "cash").strip().lower()
    comment_s = str(comment or "")
    is_internal_balance = payment_method_ui == "balance" or "[Оплата: внутренний счет]" in comment_s

    comment = _validate_order_comment(comment)
    addr_out: Optional[str] = None
    if delivery_type == "delivery":
        addr_out = _validate_order_address(address)
    elif address and str(address).strip():
        addr_out = _validate_order_address(address)
    if is_internal_balance or pm == "card":
        payment_status_init = "paid"
    elif pm == "cash":
        payment_status_init = "pending"
    else:
        payment_status_init = "pending"

    with db_conn() as conn, conn.cursor() as cur:
        if tid is not None and cert_code and discount_amount > 0:
            if _certificate_discount_percent(cur, cert_code) is None:
                json_error("Некорректный код сертификата", 400)
            cur.execute(
                "SELECT 1 FROM certificate_redemptions WHERE telegram_id = %s AND code = %s",
                (tid, cert_code),
            )
            if cur.fetchone():
                json_error("Сертификат уже был использован", 400)

        cur.execute("SELECT COUNT(*) as cnt FROM orders")
        count = int(cur.fetchone()["cnt"]) + 1
        order_number = f"AURUM-{datetime.now().year}-{str(count).zfill(4)}"

        cur.execute(
            """
            INSERT INTO orders (
                user_id, order_number, delivery_type, full_name, phone, address, comment,
                total_amount, payment_method, payment_status, customer_telegram_id, telegram_username
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                user_id,
                order_number,
                delivery_type,
                full_name,
                phone,
                addr_out,
                comment,
                total_amount,
                payment_method,
                payment_status_init,
                tid,
                telegram_username,
            ),
        )
        order_id = cur.fetchone()["id"]

        for item in items:
            product_id = item.get("product_id")
            item_type = item.get("item_type", "product")
            if item_type != "product":
                product_id = None

            if item_type == "product" and product_id is not None:
                cur.execute("SELECT id FROM products WHERE id = %s", (product_id,))
                if not cur.fetchone():
                    product_id = None

            config_data = item.get("config_data")
            cur.execute(
                """
                INSERT INTO order_items (order_id, product_id, item_type, item_name, item_specs, quantity, unit_price, total_price, config_data)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    order_id,
                    product_id,
                    item_type,
                    item.get("item_name", "Без названия"),
                    item.get("item_specs"),
                    int(item.get("quantity", 1)),
                    float(item.get("unit_price", 0)),
                    float(item.get("total_price", 0)),
                    json.dumps(config_data, ensure_ascii=False) if config_data is not None else None,
                ),
            )

        if tid is not None and cert_code and discount_amount > 0:
            cur.execute(
                """
                INSERT INTO certificate_redemptions (telegram_id, code, order_id)
                VALUES (%s, %s, %s)
                """,
                (tid, cert_code, int(order_id)),
            )
            cur.execute("DELETE FROM certificate_pending WHERE telegram_id = %s", (tid,))

        uid_for_ledger = int(user_id) if user_id is not None else None
        if tid is not None and bonus_used > 0:
            cur.execute(
                """
                INSERT INTO bonus_ledger (telegram_id, user_id, order_id, order_number, entry_type, amount, note)
                VALUES (%s, %s, %s, %s, 'spend', %s, %s)
                """,
                (
                    tid,
                    uid_for_ledger,
                    int(order_id),
                    order_number,
                    bonus_used,
                    "Списание бонусов при оплате заказа",
                ),
            )
        if tid is not None and bonus_earned > 0:
            cur.execute(
                """
                INSERT INTO bonus_ledger (telegram_id, user_id, order_id, order_number, entry_type, amount, note)
                VALUES (%s, %s, %s, %s, 'earn', %s, %s)
                """,
                (
                    tid,
                    uid_for_ledger,
                    int(order_id),
                    order_number,
                    bonus_earned,
                    "Начисление бонусов за заказ (категория 4K)",
                ),
            )

        conn.commit()

    _notify_admins_new_order(
        order_number=order_number,
        full_name=full_name,
        phone=phone,
        total_amount=total_amount,
        order_status="new",
        payment_status=payment_status_init,
        delivery_type=delivery_type,
        customer_telegram_id=tid,
        telegram_username=telegram_username,
        items_count=len(items),
    )
    _notify_customer_new_order(
        order_number=order_number,
        total_amount=total_amount,
        customer_telegram_id=tid,
        delivery_type=delivery_type,
        payment_method=pm,
        payment_status=payment_status_init,
        is_internal_balance=is_internal_balance,
    )

    response = {"id": int(order_id), "order_number": order_number}
    return {"success": True, "data": response, "order": response, "message": "Заказ успешно сохранён"}


@app.post("/api/orders")
def orders_post(
    request: Request,
    payload: dict[str, Any] = Body(...),
    id: Optional[int] = Query(default=None),
    action: Optional[str] = Query(default=None),
):
    if action == "update" and id is not None:
        require_admin(request)
        return _orders_admin_update(id, payload)
    return _orders_create(payload)


ROOT_DIR = Path(__file__).resolve().parent.parent


@app.on_event("startup")
def app_startup() -> None:
    ensure_user_state_table()
    ensure_users_is_staff_column()
    ensure_reviews_order_id_unique_index()
    ensure_orders_telegram_columns()
    ensure_products_config_json_column()
    normalize_legacy_products()


@app.get("/")
def serve_index():
    return FileResponse(ROOT_DIR / "index.html")


@app.get("/index.html")
def serve_index_html():
    """Тот же файл, что и / — относительные ссылки ../index.html из /admin/ иначе дают 404."""
    return FileResponse(ROOT_DIR / "index.html")


_admin_dir = ROOT_DIR / "admin"
if _admin_dir.is_dir():
    @app.get("/admin")
    @app.get("/admin/")
    def admin_redirect():
        return RedirectResponse(url="/admin/products.html", status_code=302)

    app.mount("/admin", StaticFiles(directory=str(_admin_dir)), name="admin_static")
else:
    # Без папки admin uvicorn не должен падать (например, свежий клон до копирования статики).
    @app.get("/admin")
    @app.get("/admin/")
    def admin_missing():
        json_error("Папка admin/ не найдена. Добавьте admin/products.html и admin/orders.html.", 503)

app.mount("/photo", StaticFiles(directory=str(ROOT_DIR / "photo")), name="photo")
app.mount("/js", StaticFiles(directory=str(ROOT_DIR / "js")), name="js")

