import json
import os
from datetime import datetime
from typing import Any, Optional

from pathlib import Path

from dotenv import load_dotenv
from fastapi import Body, FastAPI, HTTPException, Query
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


def json_success(data: Any, alias: Optional[str] = None, status: int = 200) -> dict[str, Any]:
    payload: dict[str, Any] = {"success": True, "data": data}
    if alias:
        payload[alias] = data
    return payload


def json_error(message: str, status: int = 400):
    raise HTTPException(status_code=status, detail=message)


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


@app.get("/api/health")
@app.get("/health")
def health() -> dict[str, Any]:
    return {"ok": True}


@app.get("/api/categories")
@app.get("/api/categories.php")
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
@app.get("/api/products.php")
def products_get(
    category: Optional[str] = Query(default=None),
    id: Optional[int] = Query(default=None),
    admin: Optional[str] = Query(default=None),
    admin_mode: Optional[str] = Query(default=None),
):
    with db_conn() as conn, conn.cursor() as cur:
        if id is not None:
            cur.execute(
                """
                SELECT id, name, price, image, cpu, gpu, description
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
                SELECT id, name, price, image, cpu, gpu, description
                FROM products
                WHERE category_id = %s AND is_active = true
                ORDER BY id ASC
                """,
                (category,),
            )
            products = cur.fetchall()
            return json_success(products, "products")

        show_all = (admin == "1") or (admin_mode == "true")
        if show_all:
            cur.execute(
                """
                SELECT id, name, price, image, cpu, gpu, category_id, description, is_active
                FROM products
                ORDER BY category_id, id
                """
            )
        else:
            cur.execute(
                """
                SELECT id, name, price, image, cpu, gpu, category_id, description, is_active
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


def _products_admin_update(product_id: int, data: dict[str, Any]) -> dict[str, Any]:
    fields: list[str] = []
    values: list[Any] = []
    if "category_id" in data:
        fields.append("category_id = %s")
        values.append(data["category_id"])
    if "name" in data:
        fields.append("name = %s")
        values.append(data["name"])
    if "price" in data:
        fields.append("price = %s")
        values.append(float(data["price"]))
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
    if not fields:
        json_error("Нет полей для обновления", 400)
    values.append(product_id)
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id FROM products WHERE id = %s", (product_id,))
        if not cur.fetchone():
            json_error("Товар не найден", 404)
        cur.execute("UPDATE products SET " + ", ".join(fields) + " WHERE id = %s", values)
        cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        product = cur.fetchone()
        conn.commit()
    return {"success": True, "data": product, "message": "Товар успешно обновлен"}


def _products_admin_create(data: dict[str, Any]) -> JSONResponse:
    category_id = data.get("category_id")
    name = data.get("name")
    price = data.get("price")
    if not category_id or not name or price is None:
        json_error("Обязательные поля: category_id, name, price", 400)
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id FROM categories WHERE id = %s", (category_id,))
        if not cur.fetchone():
            json_error("Категория не найдена", 400)
        cur.execute(
            """
            INSERT INTO products (category_id, name, price, image, cpu, gpu, description, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                category_id,
                name,
                float(price),
                data.get("image"),
                data.get("cpu"),
                data.get("gpu"),
                data.get("description"),
                _coerce_bool(data.get("is_active", True)),
            ),
        )
        new_id = cur.fetchone()["id"]
        cur.execute("SELECT * FROM products WHERE id = %s", (new_id,))
        product = cur.fetchone()
        conn.commit()
    return JSONResponse(
        status_code=201,
        content={"success": True, "data": product, "message": "Товар успешно создан"},
    )


@app.post("/api/products")
@app.post("/api/products.php")
def products_post(
    payload: dict[str, Any] = Body(...),
    id: Optional[int] = Query(default=None),
    action: Optional[str] = Query(default=None),
):
    if action == "update" and id is not None:
        return _products_admin_update(id, payload)
    res = _products_admin_create(payload)
    return res


@app.delete("/api/products")
@app.delete("/api/products.php")
def products_delete(id: int = Query(..., description="ID товара")):
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM products WHERE id = %s RETURNING id", (id,))
        if not cur.fetchone():
            json_error("Товар не найден", 404)
        conn.commit()
    return {"success": True, "message": "Товар успешно удален из базы данных"}


@app.get("/api/reviews")
@app.get("/api/reviews.php")
def reviews_get(
    user_id: Optional[int] = Query(default=None),
    product_id: Optional[int] = Query(default=None),
    order_id: Optional[int] = Query(default=None),
    published: Optional[str] = Query(default=None),
):
    where = []
    params: list[Any] = []
    if user_id is not None:
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
    return json_success(reviews, "reviews")


@app.post("/api/reviews")
@app.post("/api/reviews.php")
def reviews_post(payload: ReviewCreatePayload):
    if payload.rating < 1 or payload.rating > 5:
        json_error("Рейтинг должен быть от 1 до 5", 400)

    with db_conn() as conn, conn.cursor() as cur:
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


@app.get("/api/users")
@app.get("/api/users.php")
def users_get(telegram_id: Optional[int] = Query(default=None)):
    if not telegram_id:
        json_error("telegram_id обязателен", 400)
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, telegram_id, first_name, last_name, username, phone, full_name, address, created_at, updated_at
            FROM users
            WHERE telegram_id = %s
            """,
            (telegram_id,),
        )
        user = cur.fetchone()
    return {"success": True, "user": user}


@app.post("/api/users")
@app.post("/api/users.php")
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
            SELECT id, telegram_id, first_name, last_name, username, phone, full_name, address, created_at, updated_at
            FROM users
            WHERE id = %s
            """,
            (user_id,),
        )
        user = cur.fetchone()
        conn.commit()
    return {"success": True, "user": user, "message": "Пользователь сохранён"}


@app.get("/api/orders")
@app.get("/api/orders.php")
def orders_get(
    user_id: Optional[int] = Query(default=None),
    telegram_id: Optional[int] = Query(default=None),
    id: Optional[int] = Query(default=None),
    admin: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
):
    with db_conn() as conn, conn.cursor() as cur:
        if admin == "1" and id is None and user_id is None and telegram_id is None:
            sql = """
                SELECT o.*, u.phone as user_phone, u.full_name as user_name
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

        if user_id is not None:
            cur.execute("SELECT * FROM orders WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
            orders = cur.fetchall()
            for order in orders:
                cur.execute("SELECT * FROM order_items WHERE order_id = %s", (order["id"],))
                order["items"] = cur.fetchall()
            return {"success": True, "data": orders, "orders": orders}

    json_error("Необходим параметр user_id, telegram_id, id или admin=1", 400)
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
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id FROM orders WHERE id = %s", (order_id,))
        if not cur.fetchone():
            json_error("Заказ не найден", 404)
        cur.execute("UPDATE orders SET " + ", ".join(fields) + " WHERE id = %s", values)
        cur.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
        order = cur.fetchone()
        cur.execute("SELECT * FROM order_items WHERE order_id = %s", (order_id,))
        order["items"] = cur.fetchall()
        conn.commit()
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

    if not items or not full_name or not phone or total_amount <= 0:
        json_error("Обязательные поля не заполнены", 400)
    if delivery_type == "delivery" and not (address and str(address).strip()):
        json_error("Адрес доставки обязателен для заказа с доставкой", 400)

    with db_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) as cnt FROM orders")
        count = int(cur.fetchone()["cnt"]) + 1
        order_number = f"AURUM-{datetime.now().year}-{str(count).zfill(4)}"

        cur.execute(
            """
            INSERT INTO orders (user_id, order_number, delivery_type, full_name, phone, address, comment, total_amount, payment_method)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (user_id, order_number, delivery_type, full_name, phone, address, comment, total_amount, payment_method),
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

        conn.commit()

    response = {"id": int(order_id), "order_number": order_number}
    return {"success": True, "data": response, "order": response, "message": "Заказ успешно сохранён"}


@app.post("/api/orders")
@app.post("/api/orders.php")
def orders_post(
    payload: dict[str, Any] = Body(...),
    id: Optional[int] = Query(default=None),
    action: Optional[str] = Query(default=None),
):
    if action == "update" and id is not None:
        return _orders_admin_update(id, payload)
    return _orders_create(payload)


ROOT_DIR = Path(__file__).resolve().parent.parent


@app.get("/")
def serve_index():
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

