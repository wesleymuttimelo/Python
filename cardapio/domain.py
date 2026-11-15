import re
import unicodedata
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from urllib.parse import quote

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
BILLING_DAYS = 30
BILLING_SOON_DAYS = 3
MAX_QUANTITY = 20


class CardapioError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class NotFoundError(CardapioError):
    def __init__(self, message: str = "Não encontrado.") -> None:
        super().__init__(message, 404)


class ClosedMenuError(CardapioError):
    def __init__(self) -> None:
        super().__init__("Este cardápio está pausado.", 403)


@dataclass(frozen=True)
class Restaurant:
    id: int
    slug: str
    name: str
    whatsapp: str
    city: str
    category: str
    plan_status: str
    trial_ends_on: date
    paid_until: date | None
    monthly_price_cents: int
    is_demo: bool
    created_on: date


@dataclass(frozen=True)
class Category:
    id: int
    restaurant_id: int
    name: str
    position: int


@dataclass(frozen=True)
class Item:
    id: int
    restaurant_id: int
    category_id: int
    name: str
    description: str
    price_cents: int
    available: bool
    position: int


@dataclass(frozen=True)
class OrderLine:
    item_id: int
    name: str
    quantity: int
    unit_price_cents: int

    @property
    def total_cents(self) -> int:
        return self.quantity * self.unit_price_cents


@dataclass(frozen=True)
class Order:
    id: int
    restaurant_id: int
    customer_name: str
    customer_phone: str
    note: str
    total_cents: int
    lines: tuple[OrderLine, ...]
    whatsapp_url: str
    created_at: str


@dataclass(frozen=True)
class Lead:
    id: int
    name: str
    whatsapp: str
    business_name: str
    city: str
    created_at: str


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)[:40].strip("-")
    return validate_slug(slug)


def validate_slug(slug: str) -> str:
    if not SLUG_RE.match(slug) or not 3 <= len(slug) <= 40:
        raise CardapioError(
            "O link deve ter de 3 a 40 letras minúsculas, números ou hífen."
        )
    return slug


def format_brl(cents: int) -> str:
    sign = "-" if cents < 0 else ""
    amount = abs(cents)
    return f"{sign}R$ {amount // 100},{amount % 100:02d}"


def parse_price_to_cents(raw: str) -> int:
    text = raw.strip().replace("R$", "").replace(" ", "")
    if not text:
        raise CardapioError("Informe o preço.")
    if "," in text:
        text = text.replace(".", "").replace(",", ".")
    try:
        value = Decimal(text)
    except InvalidOperation as exc:
        raise CardapioError("Preço inválido. Use 22,00.") from exc
    if value < 0 or value > Decimal("10000"):
        raise CardapioError("O preço deve ficar entre R$ 0,00 e R$ 10.000,00.")
    return int((value * 100).quantize(Decimal("1")))


def normalize_whatsapp(raw: str) -> str:
    digits = "".join(character for character in raw if character.isdigit())
    if digits.startswith("55") and len(digits) in (12, 13):
        return digits
    if len(digits) in (10, 11):
        return "55" + digits
    raise CardapioError("Informe um WhatsApp com DDD. Exemplo: 11999998888.")


def clean_text(value: str, *, empty_message: str, max_length: int, too_long: str) -> str:
    text = " ".join(value.split())
    if not text:
        raise CardapioError(empty_message)
    if len(text) > max_length:
        raise CardapioError(too_long)
    return text


def menu_is_open(restaurant: Restaurant, today: date) -> bool:
    if restaurant.plan_status == "paused":
        return False
    if restaurant.paid_until is not None and restaurant.paid_until >= today:
        return True
    if restaurant.plan_status == "trial":
        return restaurant.trial_ends_on >= today
    return False


def access_ends_on(restaurant: Restaurant) -> date | None:
    dates = [restaurant.trial_ends_on] if restaurant.plan_status == "trial" else []
    if restaurant.paid_until is not None:
        dates.append(restaurant.paid_until)
    if not dates:
        return None
    return max(dates)


def needs_billing(restaurant: Restaurant, today: date) -> bool:
    if restaurant.is_demo:
        return False
    if restaurant.plan_status == "paused":
        return True
    end = access_ends_on(restaurant)
    if end is None:
        return True
    return end <= today + timedelta(days=BILLING_SOON_DAYS)


def counts_as_mrr(restaurant: Restaurant, today: date) -> bool:
    return (
        not restaurant.is_demo
        and restaurant.plan_status == "active"
        and menu_is_open(restaurant, today)
    )


def extend_paid_until(restaurant: Restaurant, today: date, days: int = BILLING_DAYS) -> date:
    start_candidates = [today]
    if restaurant.paid_until is not None:
        start_candidates.append(restaurant.paid_until)
    if restaurant.plan_status == "trial":
        start_candidates.append(restaurant.trial_ends_on)
    start = max(start_candidates)
    if start < today:
        start = today
    return start + timedelta(days=days)


def build_order_text(
    restaurant_name: str,
    lines: list[OrderLine],
    total_cents: int,
    customer_name: str,
    customer_phone: str,
    note: str,
) -> str:
    rows = [
        f"{line.quantity}x {line.name} — {format_brl(line.total_cents)}"
        for line in lines
    ]
    parts = [
        f"Olá! Quero fazer um pedido em {restaurant_name}:",
        "",
        *rows,
        "",
        f"Total: {format_brl(total_cents)}",
        f"Nome: {customer_name}",
        f"WhatsApp: {customer_phone}",
    ]
    if note.strip():
        parts.append(f"Obs: {note.strip()}")
    parts.append("")
    parts.append("Pagamento combinado direto com a loja.")
    return "\n".join(parts)


def build_whatsapp_url(phone_digits: str, text: str) -> str:
    return f"https://wa.me/{phone_digits}?text={quote(text)}"


def public_menu_url(base_url: str, slug: str) -> str:
    return f"{base_url.rstrip('/')}/r/{slug}"


def billing_message(
    restaurant: Restaurant,
    *,
    menu_url: str,
    pix_key: str,
    pix_name: str,
    operator_name: str,
) -> str:
    return "\n".join(
        [
            f"Oi! Aqui é da {operator_name}.",
            f"O cardápio de {restaurant.name} segue no ar: {menu_url}",
            f"A mensalidade é {format_brl(restaurant.monthly_price_cents)} via Pix.",
            f"Chave: {pix_key}" if pix_key else "Chave Pix: configure CARDAPIO_PIX_KEY.",
            f"Nome: {pix_name}" if pix_name else "",
            "Depois do pagamento me avise por aqui.",
        ]
    ).strip()
