import secrets
import sqlite3
from datetime import date, datetime, timedelta, timezone

from cardapio.config import CardapioSettings
from cardapio.domain import (
    MAX_QUANTITY,
    CardapioError,
    Category,
    ClosedMenuError,
    Item,
    Lead,
    NotFoundError,
    Order,
    OrderLine,
    Restaurant,
    billing_message,
    build_order_text,
    build_whatsapp_url,
    clean_text,
    counts_as_mrr,
    extend_paid_until,
    menu_is_open,
    needs_billing,
    normalize_source,
    normalize_whatsapp,
    parse_price_to_cents,
    public_menu_url,
    slugify,
    validate_slug,
)
from cardapio.repository import Repository


class CardapioService:
    def __init__(
        self,
        repository: Repository,
        settings: CardapioSettings,
        today_fn=date.today,
    ) -> None:
        self.repository = repository
        self.settings = settings
        self.today_fn = today_fn

    def today(self) -> date:
        return self.today_fn()

    def seed_demo(self) -> None:
        if self.repository.get_restaurant_by_slug("demo") is not None:
            return
        today = self.today()
        restaurant = self.repository.insert_restaurant(
            slug="demo",
            name="Marmitas da Ana",
            whatsapp="5511999990000",
            city="São Paulo",
            category="Marmitas",
            plan_status="active",
            trial_ends_on=today,
            paid_until=today + timedelta(days=3650),
            monthly_price_cents=0,
            is_demo=True,
            created_on=today,
        )
        meals = self.repository.insert_category(restaurant.id, "Marmitas")
        drinks = self.repository.insert_category(restaurant.id, "Bebidas")
        self.repository.insert_item(
            restaurant_id=restaurant.id,
            category_id=meals.id,
            name="Frango grelhado",
            description="Arroz, feijão e salada",
            price_cents=2200,
        )
        self.repository.insert_item(
            restaurant_id=restaurant.id,
            category_id=meals.id,
            name="Carne de panela",
            description="Arroz, feijão e farofa",
            price_cents=2400,
        )
        self.repository.insert_item(
            restaurant_id=restaurant.id,
            category_id=drinks.id,
            name="Suco de laranja",
            description="Copo de 300 ml",
            price_cents=800,
        )

    def create_restaurant(
        self,
        *,
        name: str,
        whatsapp: str,
        city: str,
        category: str,
        slug: str = "",
        monthly_price: str = "",
        source: str = "direto",
    ) -> Restaurant:
        clean_name = clean_text(
            name,
            empty_message="Informe o nome da loja.",
            max_length=80,
            too_long="O nome da loja é longo demais.",
        )
        chosen_slug = validate_slug(slug) if slug.strip() else slugify(clean_name)
        if chosen_slug == "demo":
            raise CardapioError("O link demo está reservado para o exemplo.")
        price_cents = (
            parse_price_to_cents(monthly_price)
            if monthly_price.strip()
            else self.settings.default_price_cents
        )
        today = self.today()
        try:
            return self.repository.insert_restaurant(
                slug=chosen_slug,
                name=clean_name,
                whatsapp=normalize_whatsapp(whatsapp),
                city=clean_text(
                    city,
                    empty_message="Informe a cidade.",
                    max_length=60,
                    too_long="A cidade é longa demais.",
                ),
                category=clean_text(
                    category,
                    empty_message="Informe o ramo. Exemplo: marmitas.",
                    max_length=40,
                    too_long="O ramo é longo demais.",
                ),
                plan_status="trial",
                trial_ends_on=today + timedelta(days=self.settings.trial_days),
                paid_until=None,
                monthly_price_cents=price_cents,
                is_demo=False,
                created_on=today,
                source=normalize_source(source),
            )
        except sqlite3.IntegrityError as exc:
            raise CardapioError("Esse link já está em uso.") from exc

    def start_self_serve(
        self,
        *,
        owner_name: str,
        business_name: str,
        whatsapp: str,
        city: str,
        category: str,
        source: str,
    ) -> Restaurant:
        chosen_source = normalize_source(source)
        base_slug = slugify(business_name)
        if base_slug == "demo":
            base_slug = "cardapio"
        restaurant = self.create_restaurant(
            name=business_name,
            whatsapp=whatsapp,
            city=city,
            category=category,
            slug=self._available_slug(base_slug),
            source=chosen_source,
        )
        token = secrets.token_urlsafe(18)
        self.repository.set_manage_token(restaurant.id, token)
        self.repository.insert_category(restaurant.id, "Cardápio")
        self.create_lead(
            name=owner_name,
            whatsapp=whatsapp,
            business_name=business_name,
            city=city,
            source=chosen_source,
        )
        created = self._require_restaurant(restaurant.id)
        return created

    def _available_slug(self, base: str) -> str:
        candidate = base
        for number in range(2, 30):
            if self.repository.get_restaurant_by_slug(candidate) is None:
                return candidate
            suffix = f"-{number}"
            candidate = f"{base[:40 - len(suffix)]}{suffix}"
        raise CardapioError("Não foi possível criar o link. Tente outro nome.")

    def restaurant_by_token(self, token: str) -> Restaurant:
        if not token:
            raise NotFoundError("Link da loja não encontrado.")
        restaurant = self.repository.get_restaurant_by_token(token)
        if restaurant is None:
            raise NotFoundError("Link da loja não encontrado.")
        return restaurant

    def add_category(self, restaurant_id: int, name: str) -> Category:
        self._require_restaurant(restaurant_id)
        return self.repository.insert_category(
            restaurant_id,
            clean_text(
                name,
                empty_message="Informe o nome da categoria.",
                max_length=40,
                too_long="A categoria é longa demais.",
            ),
        )

    def add_item(
        self,
        restaurant_id: int,
        *,
        category_id: int,
        name: str,
        description: str,
        price: str,
    ) -> Item:
        self._require_restaurant(restaurant_id)
        category = self.repository.get_category(category_id)
        if category is None or category.restaurant_id != restaurant_id:
            raise CardapioError("Escolha uma categoria desta loja.")
        description_text = " ".join(description.split())
        if len(description_text) > 200:
            raise CardapioError("A descrição é longa demais.")
        return self.repository.insert_item(
            restaurant_id=restaurant_id,
            category_id=category_id,
            name=clean_text(
                name,
                empty_message="Informe o nome do item.",
                max_length=80,
                too_long="O nome do item é longo demais.",
            ),
            description=description_text,
            price_cents=parse_price_to_cents(price),
        )

    def toggle_item(self, item_id: int) -> Item:
        item = self.repository.get_item(item_id)
        if item is None:
            raise NotFoundError("Item não encontrado.")
        self.repository.set_item_available(item_id, not item.available)
        updated = self.repository.get_item(item_id)
        if updated is None:
            raise NotFoundError("Item não encontrado.")
        return updated

    def confirm_payment(self, restaurant_id: int) -> Restaurant:
        restaurant = self._require_restaurant(restaurant_id)
        paid_until = extend_paid_until(restaurant, self.today())
        self.repository.update_plan(
            restaurant_id,
            plan_status="active",
            paid_until=paid_until,
        )
        return self._require_restaurant(restaurant_id)

    def pause(self, restaurant_id: int) -> Restaurant:
        restaurant = self._require_restaurant(restaurant_id)
        self.repository.update_plan(
            restaurant_id,
            plan_status="paused",
            paid_until=restaurant.paid_until,
        )
        return self._require_restaurant(restaurant_id)

    def resume(self, restaurant_id: int) -> Restaurant:
        restaurant = self._require_restaurant(restaurant_id)
        today = self.today()
        if restaurant.paid_until is not None and restaurant.paid_until >= today:
            status = "active"
        elif restaurant.trial_ends_on >= today:
            status = "trial"
        else:
            raise CardapioError("A mensalidade está vencida. Confirme o Pix antes de reabrir.")
        self.repository.update_plan(
            restaurant_id,
            plan_status=status,
            paid_until=restaurant.paid_until,
        )
        return self._require_restaurant(restaurant_id)

    def place_order(
        self,
        slug: str,
        *,
        customer_name: str,
        customer_phone: str,
        note: str,
        quantities: dict[int, int],
    ) -> Order:
        restaurant = self.repository.get_restaurant_by_slug(slug)
        if restaurant is None:
            raise NotFoundError("Cardápio não encontrado.")
        if not menu_is_open(restaurant, self.today()):
            raise ClosedMenuError()
        if len(quantities) > 100:
            raise CardapioError("Pedido grande demais.")
        lines: list[OrderLine] = []
        for item_id, quantity in quantities.items():
            if quantity == 0:
                continue
            if quantity < 0 or quantity > MAX_QUANTITY:
                raise CardapioError(f"A quantidade deve ficar entre 0 e {MAX_QUANTITY}.")
            item = self.repository.get_item(item_id)
            if item is None or item.restaurant_id != restaurant.id:
                raise CardapioError("Há um item que não pertence a este cardápio.")
            if not item.available:
                raise CardapioError(f"{item.name} está esgotado.")
            lines.append(
                OrderLine(
                    item_id=item.id,
                    name=item.name,
                    quantity=quantity,
                    unit_price_cents=item.price_cents,
                )
            )
        if not lines:
            raise CardapioError("Escolha pelo menos um item.")
        name = clean_text(
            customer_name,
            empty_message="Informe seu nome.",
            max_length=80,
            too_long="O nome é longo demais.",
        )
        phone = normalize_whatsapp(customer_phone)
        note_text = " ".join(note.split())
        if len(note_text) > 300:
            raise CardapioError("A observação é longa demais.")
        total = sum(line.total_cents for line in lines)
        text = build_order_text(restaurant.name, lines, total, name, phone, note_text)
        return self.repository.insert_order(
            restaurant_id=restaurant.id,
            customer_name=name,
            customer_phone=phone,
            note=note_text,
            total_cents=total,
            lines=lines,
            whatsapp_url=build_whatsapp_url(restaurant.whatsapp, text),
            created_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        )

    def create_lead(
        self,
        *,
        name: str,
        whatsapp: str,
        business_name: str,
        city: str,
        source: str = "direto",
    ) -> Lead:
        return self.repository.insert_lead(
            name=clean_text(
                name,
                empty_message="Informe seu nome.",
                max_length=80,
                too_long="O nome é longo demais.",
            ),
            whatsapp=normalize_whatsapp(whatsapp),
            business_name=clean_text(
                business_name,
                empty_message="Informe o nome do negócio.",
                max_length=80,
                too_long="O nome do negócio é longo demais.",
            ),
            city=clean_text(
                city,
                empty_message="Informe a cidade.",
                max_length=60,
                too_long="A cidade é longa demais.",
            ),
            created_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            source=normalize_source(source),
        )

    def delete_order(self, order_id: int) -> int:
        order = self.repository.get_order(order_id)
        if order is None:
            raise NotFoundError("Pedido não encontrado.")
        self.repository.delete_order(order_id)
        return order.restaurant_id

    def public_menu(self, slug: str) -> tuple[Restaurant, list[tuple[Category, list[Item]]], bool]:
        restaurant = self.repository.get_restaurant_by_slug(slug)
        if restaurant is None:
            raise NotFoundError("Cardápio não encontrado.")
        groups = self._groups(restaurant.id)
        return restaurant, groups, menu_is_open(restaurant, self.today())

    def dashboard(self) -> dict:
        today = self.today()
        restaurants = self.repository.list_restaurants()
        mrr = sum(
            restaurant.monthly_price_cents
            for restaurant in restaurants
            if counts_as_mrr(restaurant, today)
        )
        due = [restaurant for restaurant in restaurants if needs_billing(restaurant, today)]
        month = today.strftime("%Y-%m")
        return {
            "restaurants": restaurants,
            "due": due,
            "mrr_cents": mrr,
            "open_count": sum(1 for restaurant in restaurants if menu_is_open(restaurant, today)),
            "orders_this_month": self.repository.count_orders_in_month(month),
            "leads": self.repository.list_leads(),
        }

    def billing_text(self, restaurant: Restaurant) -> str:
        return billing_message(
            restaurant,
            menu_url=public_menu_url(self.settings.public_base, restaurant.slug),
            pix_key=self.settings.pix_key,
            pix_name=self.settings.pix_name,
            operator_name=self.settings.operator_name,
        )

    def billing_link(self, restaurant: Restaurant) -> str:
        return build_whatsapp_url(restaurant.whatsapp, self.billing_text(restaurant))

    def _groups(self, restaurant_id: int) -> list[tuple[Category, list[Item]]]:
        categories = self.repository.list_categories(restaurant_id)
        return [
            (category, self.repository.list_items_for_category(category.id))
            for category in categories
        ]

    def _require_restaurant(self, restaurant_id: int) -> Restaurant:
        restaurant = self.repository.get_restaurant(restaurant_id)
        if restaurant is None:
            raise NotFoundError("Loja não encontrada.")
        return restaurant
