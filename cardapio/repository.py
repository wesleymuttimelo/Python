import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from pathlib import Path

from cardapio.domain import (
    Category,
    Item,
    Lead,
    Order,
    OrderLine,
    Restaurant,
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS restaurants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    whatsapp TEXT NOT NULL,
    city TEXT NOT NULL DEFAULT '',
    category TEXT NOT NULL DEFAULT '',
    plan_status TEXT NOT NULL,
    trial_ends_on TEXT NOT NULL,
    paid_until TEXT,
    monthly_price_cents INTEGER NOT NULL,
    is_demo INTEGER NOT NULL DEFAULT 0,
    created_on TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'direto',
    manage_token TEXT
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_id INTEGER NOT NULL REFERENCES restaurants(id),
    name TEXT NOT NULL,
    position INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_id INTEGER NOT NULL REFERENCES restaurants(id),
    category_id INTEGER NOT NULL REFERENCES categories(id),
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    price_cents INTEGER NOT NULL,
    available INTEGER NOT NULL DEFAULT 1,
    position INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_id INTEGER NOT NULL REFERENCES restaurants(id),
    customer_name TEXT NOT NULL,
    customer_phone TEXT NOT NULL,
    note TEXT NOT NULL DEFAULT '',
    total_cents INTEGER NOT NULL,
    items_json TEXT NOT NULL,
    whatsapp_url TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    whatsapp TEXT NOT NULL,
    business_name TEXT NOT NULL,
    city TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'direto'
);
"""


def _add_column(connection: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    existing = {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}
    if column not in existing:
        connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def _date_or_none(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


def restaurant_from_row(row: sqlite3.Row) -> Restaurant:
    return Restaurant(
        id=row["id"],
        slug=row["slug"],
        name=row["name"],
        whatsapp=row["whatsapp"],
        city=row["city"],
        category=row["category"],
        plan_status=row["plan_status"],
        trial_ends_on=date.fromisoformat(row["trial_ends_on"]),
        paid_until=_date_or_none(row["paid_until"]),
        monthly_price_cents=row["monthly_price_cents"],
        is_demo=bool(row["is_demo"]),
        created_on=date.fromisoformat(row["created_on"]),
        source=row["source"] or "direto",
        manage_token=row["manage_token"],
    )


def category_from_row(row: sqlite3.Row) -> Category:
    return Category(
        id=row["id"],
        restaurant_id=row["restaurant_id"],
        name=row["name"],
        position=row["position"],
    )


def item_from_row(row: sqlite3.Row) -> Item:
    return Item(
        id=row["id"],
        restaurant_id=row["restaurant_id"],
        category_id=row["category_id"],
        name=row["name"],
        description=row["description"],
        price_cents=row["price_cents"],
        available=bool(row["available"]),
        position=row["position"],
    )


def order_from_row(row: sqlite3.Row) -> Order:
    payload = json.loads(row["items_json"])
    lines = tuple(
        OrderLine(
            item_id=line["item_id"],
            name=line["name"],
            quantity=line["quantity"],
            unit_price_cents=line["unit_price_cents"],
        )
        for line in payload
    )
    return Order(
        id=row["id"],
        restaurant_id=row["restaurant_id"],
        customer_name=row["customer_name"],
        customer_phone=row["customer_phone"],
        note=row["note"],
        total_cents=row["total_cents"],
        lines=lines,
        whatsapp_url=row["whatsapp_url"],
        created_at=row["created_at"],
    )


def lead_from_row(row: sqlite3.Row) -> Lead:
    return Lead(
        id=row["id"],
        name=row["name"],
        whatsapp=row["whatsapp"],
        business_name=row["business_name"],
        city=row["city"],
        created_at=row["created_at"],
        source=row["source"] or "direto",
    )


class Repository:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    @contextmanager
    def session(self) -> Iterator[sqlite3.Connection]:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.db_path, timeout=5)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def init(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.db_path, timeout=5)
        try:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.executescript(SCHEMA)
            _add_column(connection, "restaurants", "source", "TEXT NOT NULL DEFAULT 'direto'")
            _add_column(connection, "restaurants", "manage_token", "TEXT")
            _add_column(connection, "leads", "source", "TEXT NOT NULL DEFAULT 'direto'")
            connection.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS restaurants_manage_token ON restaurants(manage_token)"
            )
        finally:
            connection.close()

    def list_restaurants(self) -> list[Restaurant]:
        with self.session() as connection:
            rows = connection.execute(
                "SELECT * FROM restaurants ORDER BY is_demo, name COLLATE NOCASE"
            ).fetchall()
            return [restaurant_from_row(row) for row in rows]

    def get_restaurant(self, restaurant_id: int) -> Restaurant | None:
        with self.session() as connection:
            row = connection.execute(
                "SELECT * FROM restaurants WHERE id = ?",
                (restaurant_id,),
            ).fetchone()
            return restaurant_from_row(row) if row else None

    def get_restaurant_by_slug(self, slug: str) -> Restaurant | None:
        with self.session() as connection:
            row = connection.execute(
                "SELECT * FROM restaurants WHERE slug = ?",
                (slug,),
            ).fetchone()
            return restaurant_from_row(row) if row else None

    def get_restaurant_by_token(self, token: str) -> Restaurant | None:
        with self.session() as connection:
            row = connection.execute(
                "SELECT * FROM restaurants WHERE manage_token = ?",
                (token,),
            ).fetchone()
            return restaurant_from_row(row) if row else None

    def set_manage_token(self, restaurant_id: int, token: str) -> None:
        with self.session() as connection:
            connection.execute(
                "UPDATE restaurants SET manage_token = ? WHERE id = ?",
                (token, restaurant_id),
            )

    def insert_restaurant(
        self,
        *,
        slug: str,
        name: str,
        whatsapp: str,
        city: str,
        category: str,
        plan_status: str,
        trial_ends_on: date,
        paid_until: date | None,
        monthly_price_cents: int,
        is_demo: bool,
        created_on: date,
        source: str = "direto",
        manage_token: str | None = None,
    ) -> Restaurant:
        with self.session() as connection:
            cursor = connection.execute(
                """
                INSERT INTO restaurants (
                    slug, name, whatsapp, city, category, plan_status,
                    trial_ends_on, paid_until, monthly_price_cents, is_demo, created_on,
                    source, manage_token
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    slug,
                    name,
                    whatsapp,
                    city,
                    category,
                    plan_status,
                    trial_ends_on.isoformat(),
                    paid_until.isoformat() if paid_until else None,
                    monthly_price_cents,
                    int(is_demo),
                    created_on.isoformat(),
                    source,
                    manage_token,
                ),
            )
            row = connection.execute(
                "SELECT * FROM restaurants WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()
            return restaurant_from_row(row)

    def update_plan(
        self,
        restaurant_id: int,
        *,
        plan_status: str,
        paid_until: date | None,
    ) -> None:
        with self.session() as connection:
            connection.execute(
                """
                UPDATE restaurants
                SET plan_status = ?, paid_until = ?
                WHERE id = ?
                """,
                (
                    plan_status,
                    paid_until.isoformat() if paid_until else None,
                    restaurant_id,
                ),
            )

    def set_trial_end(self, restaurant_id: int, trial_ends_on: date, plan_status: str) -> None:
        with self.session() as connection:
            connection.execute(
                """
                UPDATE restaurants
                SET trial_ends_on = ?, plan_status = ?, paid_until = NULL
                WHERE id = ?
                """,
                (trial_ends_on.isoformat(), plan_status, restaurant_id),
            )

    def list_categories(self, restaurant_id: int) -> list[Category]:
        with self.session() as connection:
            rows = connection.execute(
                """
                SELECT * FROM categories
                WHERE restaurant_id = ?
                ORDER BY position, id
                """,
                (restaurant_id,),
            ).fetchall()
            return [category_from_row(row) for row in rows]

    def get_category(self, category_id: int) -> Category | None:
        with self.session() as connection:
            row = connection.execute(
                "SELECT * FROM categories WHERE id = ?",
                (category_id,),
            ).fetchone()
            return category_from_row(row) if row else None

    def insert_category(self, restaurant_id: int, name: str) -> Category:
        with self.session() as connection:
            position = connection.execute(
                """
                SELECT COALESCE(MAX(position), 0) + 1 AS position
                FROM categories WHERE restaurant_id = ?
                """,
                (restaurant_id,),
            ).fetchone()["position"]
            cursor = connection.execute(
                """
                INSERT INTO categories (restaurant_id, name, position)
                VALUES (?, ?, ?)
                """,
                (restaurant_id, name, position),
            )
            row = connection.execute(
                "SELECT * FROM categories WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()
            return category_from_row(row)

    def list_items(self, restaurant_id: int) -> list[Item]:
        with self.session() as connection:
            rows = connection.execute(
                """
                SELECT * FROM items
                WHERE restaurant_id = ?
                ORDER BY position, id
                """,
                (restaurant_id,),
            ).fetchall()
            return [item_from_row(row) for row in rows]

    def list_items_for_category(self, category_id: int) -> list[Item]:
        with self.session() as connection:
            rows = connection.execute(
                """
                SELECT * FROM items
                WHERE category_id = ?
                ORDER BY position, id
                """,
                (category_id,),
            ).fetchall()
            return [item_from_row(row) for row in rows]

    def get_item(self, item_id: int) -> Item | None:
        with self.session() as connection:
            row = connection.execute(
                "SELECT * FROM items WHERE id = ?",
                (item_id,),
            ).fetchone()
            return item_from_row(row) if row else None

    def insert_item(
        self,
        *,
        restaurant_id: int,
        category_id: int,
        name: str,
        description: str,
        price_cents: int,
    ) -> Item:
        with self.session() as connection:
            position = connection.execute(
                """
                SELECT COALESCE(MAX(position), 0) + 1 AS position
                FROM items WHERE category_id = ?
                """,
                (category_id,),
            ).fetchone()["position"]
            cursor = connection.execute(
                """
                INSERT INTO items (
                    restaurant_id, category_id, name, description,
                    price_cents, available, position
                ) VALUES (?, ?, ?, ?, ?, 1, ?)
                """,
                (restaurant_id, category_id, name, description, price_cents, position),
            )
            row = connection.execute(
                "SELECT * FROM items WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()
            return item_from_row(row)

    def set_item_available(self, item_id: int, available: bool) -> None:
        with self.session() as connection:
            connection.execute(
                "UPDATE items SET available = ? WHERE id = ?",
                (int(available), item_id),
            )

    def insert_order(
        self,
        *,
        restaurant_id: int,
        customer_name: str,
        customer_phone: str,
        note: str,
        total_cents: int,
        lines: list[OrderLine],
        whatsapp_url: str,
        created_at: str,
    ) -> Order:
        payload = [
            {
                "item_id": line.item_id,
                "name": line.name,
                "quantity": line.quantity,
                "unit_price_cents": line.unit_price_cents,
            }
            for line in lines
        ]
        with self.session() as connection:
            cursor = connection.execute(
                """
                INSERT INTO orders (
                    restaurant_id, customer_name, customer_phone, note,
                    total_cents, items_json, whatsapp_url, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    restaurant_id,
                    customer_name,
                    customer_phone,
                    note,
                    total_cents,
                    json.dumps(payload, ensure_ascii=False),
                    whatsapp_url,
                    created_at,
                ),
            )
            row = connection.execute(
                "SELECT * FROM orders WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()
            return order_from_row(row)

    def get_order(self, order_id: int) -> Order | None:
        with self.session() as connection:
            row = connection.execute(
                "SELECT * FROM orders WHERE id = ?",
                (order_id,),
            ).fetchone()
            return order_from_row(row) if row else None

    def list_orders(self, restaurant_id: int, limit: int = 20) -> list[Order]:
        with self.session() as connection:
            rows = connection.execute(
                """
                SELECT * FROM orders
                WHERE restaurant_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (restaurant_id, limit),
            ).fetchall()
            return [order_from_row(row) for row in rows]

    def count_orders_in_month(self, month_prefix: str) -> int:
        with self.session() as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS total FROM orders WHERE created_at LIKE ?",
                (f"{month_prefix}%",),
            ).fetchone()
            return int(row["total"])

    def delete_order(self, order_id: int) -> None:
        with self.session() as connection:
            connection.execute("DELETE FROM orders WHERE id = ?", (order_id,))

    def insert_lead(
        self,
        *,
        name: str,
        whatsapp: str,
        business_name: str,
        city: str,
        created_at: str,
        source: str = "direto",
    ) -> Lead:
        with self.session() as connection:
            cursor = connection.execute(
                """
                INSERT INTO leads (name, whatsapp, business_name, city, created_at, source)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (name, whatsapp, business_name, city, created_at, source),
            )
            row = connection.execute(
                "SELECT * FROM leads WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()
            return lead_from_row(row)

    def list_leads(self, limit: int = 30) -> list[Lead]:
        with self.session() as connection:
            rows = connection.execute(
                "SELECT * FROM leads ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [lead_from_row(row) for row in rows]
