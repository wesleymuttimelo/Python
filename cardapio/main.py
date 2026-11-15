import io
import secrets
from urllib.parse import parse_qs

import segno
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from cardapio.config import CardapioSettings
from cardapio.domain import CardapioError, format_brl, public_menu_url
from cardapio.pages import (
    dashboard_page,
    error_page,
    landing_page,
    login_page,
    order_page,
    print_page,
    public_menu_page,
    restaurant_admin_page,
    thanks_page,
)
from cardapio.repository import Repository
from cardapio.service import CardapioService

COOKIE = "cardapio_admin"


def create_app(settings: CardapioSettings | None = None) -> FastAPI:
    settings = settings or CardapioSettings()
    repository = Repository(settings.db_path)
    repository.init()
    service = CardapioService(repository, settings)
    service.seed_demo()

    app = FastAPI(title="Cardápio Pix", version="1.0.0")
    app.state.settings = settings
    app.state.repository = repository
    app.state.service = service

    def service_of(request: Request) -> CardapioService:
        return request.app.state.service

    def settings_of(request: Request) -> CardapioSettings:
        return request.app.state.settings

    def is_admin(request: Request) -> bool:
        configured = settings_of(request).admin_token
        cookie = request.cookies.get(COOKIE, "")
        if not configured or not cookie:
            return False
        return secrets.compare_digest(cookie, configured)

    def deny_admin() -> RedirectResponse:
        return RedirectResponse("/admin/login", status_code=303)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "cardapio-pix"}

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request) -> HTMLResponse:
        price = format_brl(settings_of(request).default_price_cents)
        return HTMLResponse(landing_page(price))

    @app.post("/interessados", response_class=HTMLResponse)
    async def create_interest(request: Request) -> Response:
        form = await read_form(request)
        try:
            service_of(request).create_lead(
                name=form.get("name", ""),
                whatsapp=form.get("whatsapp", ""),
                business_name=form.get("business_name", ""),
                city=form.get("city", ""),
            )
        except CardapioError as exc:
            price = format_brl(settings_of(request).default_price_cents)
            return HTMLResponse(landing_page(price, error=exc.message), status_code=exc.status_code)
        return RedirectResponse("/obrigado", status_code=303)

    @app.get("/obrigado", response_class=HTMLResponse)
    def thanks() -> HTMLResponse:
        return HTMLResponse(thanks_page())

    @app.get("/api/cardapio/{slug}")
    def menu_api(slug: str, request: Request) -> dict:
        try:
            restaurant, groups, is_open = service_of(request).public_menu(slug)
        except CardapioError as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
        return {
            "slug": restaurant.slug,
            "name": restaurant.name,
            "is_open": is_open,
            "categories": [
                {
                    "name": category.name,
                    "items": [
                        {
                            "id": item.id,
                            "name": item.name,
                            "description": item.description,
                            "price_cents": item.price_cents,
                            "available": item.available,
                        }
                        for item in items
                    ],
                }
                for category, items in groups
            ],
        }

    @app.get("/r/{slug}", response_class=HTMLResponse)
    def show_menu(slug: str, request: Request) -> HTMLResponse:
        try:
            restaurant, groups, is_open = service_of(request).public_menu(slug)
        except CardapioError as exc:
            return HTMLResponse(error_page("Cardápio", exc.message), status_code=exc.status_code)
        return HTMLResponse(public_menu_page(restaurant, groups, is_open=is_open))

    @app.post("/r/{slug}/pedidos", response_class=HTMLResponse)
    async def place_order(slug: str, request: Request) -> Response:
        form = await read_form(request)
        try:
            order = service_of(request).place_order(
                slug,
                customer_name=form.get("customer_name", ""),
                customer_phone=form.get("customer_phone", ""),
                note=form.get("note", ""),
                quantities=quantities_from_form(form),
            )
        except CardapioError as exc:
            try:
                restaurant, groups, is_open = service_of(request).public_menu(slug)
            except CardapioError:
                return HTMLResponse(error_page("Pedido", exc.message), status_code=exc.status_code)
            return HTMLResponse(
                public_menu_page(restaurant, groups, is_open=is_open, error=exc.message),
                status_code=exc.status_code,
            )
        return RedirectResponse(f"/r/{slug}/pedidos/{order.id}", status_code=303)

    @app.get("/r/{slug}/pedidos/{order_id}", response_class=HTMLResponse)
    def show_order(slug: str, order_id: int, request: Request) -> HTMLResponse:
        service = service_of(request)
        restaurant = service.repository.get_restaurant_by_slug(slug)
        order = service.repository.get_order(order_id)
        if restaurant is None or order is None or order.restaurant_id != restaurant.id:
            return HTMLResponse(error_page("Pedido", "Pedido não encontrado."), status_code=404)
        return HTMLResponse(order_page(restaurant, order))

    @app.get("/r/{slug}/imprimir", response_class=HTMLResponse)
    def print_menu(slug: str, request: Request) -> HTMLResponse:
        restaurant = service_of(request).repository.get_restaurant_by_slug(slug)
        if restaurant is None:
            return HTMLResponse(error_page("Cardápio", "Cardápio não encontrado."), status_code=404)
        url = public_menu_url(settings_of(request).public_base, slug)
        return HTMLResponse(print_page(restaurant, url))

    @app.get("/r/{slug}/qr.svg")
    def menu_qr(slug: str, request: Request) -> Response:
        restaurant = service_of(request).repository.get_restaurant_by_slug(slug)
        if restaurant is None:
            raise HTTPException(status_code=404, detail="Cardápio não encontrado.")
        url = public_menu_url(settings_of(request).public_base, slug)
        buffer = io.BytesIO()
        segno.make(url, error="m").save(buffer, kind="svg", scale=6, border=2, xmldecl=False)
        return Response(content=buffer.getvalue(), media_type="image/svg+xml")

    @app.get("/admin/login", response_class=HTMLResponse)
    def login_form(request: Request) -> Response:
        if is_admin(request):
            return RedirectResponse("/admin", status_code=303)
        missing = not settings_of(request).admin_token
        return HTMLResponse(login_page(token_missing=missing))

    @app.post("/admin/login")
    async def login(request: Request) -> Response:
        settings = settings_of(request)
        if not settings.admin_token:
            return HTMLResponse(login_page(token_missing=True), status_code=503)
        form = await read_form(request)
        token = form.get("token", "")
        if not secrets.compare_digest(token, settings.admin_token):
            return HTMLResponse(login_page(error="Token incorreto."), status_code=401)
        response = RedirectResponse("/admin", status_code=303)
        response.set_cookie(
            COOKIE,
            settings.admin_token,
            httponly=True,
            samesite="lax",
            secure=settings.cookie_secure,
            max_age=60 * 60 * 24 * 14,
        )
        return response

    @app.post("/admin/sair")
    def logout() -> RedirectResponse:
        response = RedirectResponse("/admin/login", status_code=303)
        response.delete_cookie(COOKIE)
        return response

    @app.get("/admin", response_class=HTMLResponse)
    def dashboard(request: Request) -> Response:
        if not is_admin(request):
            return deny_admin()
        data = service_of(request).dashboard()
        price = format_brl(settings_of(request).default_price_cents)
        return HTMLResponse(dashboard_page(data, price))

    @app.post("/admin/restaurantes")
    async def create_restaurant(request: Request) -> Response:
        if not is_admin(request):
            return deny_admin()
        form = await read_form(request)
        try:
            restaurant = service_of(request).create_restaurant(
                name=form.get("name", ""),
                whatsapp=form.get("whatsapp", ""),
                city=form.get("city", ""),
                category=form.get("category", ""),
                slug=form.get("slug", ""),
                monthly_price=form.get("monthly_price", ""),
            )
        except CardapioError as exc:
            data = service_of(request).dashboard()
            price = format_brl(settings_of(request).default_price_cents)
            return HTMLResponse(
                dashboard_page(data, price, error=exc.message),
                status_code=exc.status_code,
            )
        return RedirectResponse(f"/admin/restaurantes/{restaurant.id}", status_code=303)

    @app.get("/admin/restaurantes/{restaurant_id}", response_class=HTMLResponse)
    def restaurant_admin(restaurant_id: int, request: Request) -> Response:
        if not is_admin(request):
            return deny_admin()
        return _render_restaurant(request, restaurant_id)

    @app.post("/admin/restaurantes/{restaurant_id}/categorias")
    async def add_category(restaurant_id: int, request: Request) -> Response:
        if not is_admin(request):
            return deny_admin()
        form = await read_form(request)
        try:
            service_of(request).add_category(restaurant_id, form.get("name", ""))
        except CardapioError as exc:
            return _render_restaurant(request, restaurant_id, error=exc.message, status_code=exc.status_code)
        return RedirectResponse(f"/admin/restaurantes/{restaurant_id}", status_code=303)

    @app.post("/admin/restaurantes/{restaurant_id}/itens")
    async def add_item(restaurant_id: int, request: Request) -> Response:
        if not is_admin(request):
            return deny_admin()
        form = await read_form(request)
        try:
            category_id = int(form.get("category_id", "0"))
            service_of(request).add_item(
                restaurant_id,
                category_id=category_id,
                name=form.get("name", ""),
                description=form.get("description", ""),
                price=form.get("price", ""),
            )
        except (CardapioError, ValueError) as exc:
            message = exc.message if isinstance(exc, CardapioError) else "Categoria inválida."
            status_code = exc.status_code if isinstance(exc, CardapioError) else 400
            return _render_restaurant(request, restaurant_id, error=message, status_code=status_code)
        return RedirectResponse(f"/admin/restaurantes/{restaurant_id}", status_code=303)

    @app.post("/admin/itens/{item_id}/disponibilidade")
    def toggle_item(item_id: int, request: Request) -> Response:
        if not is_admin(request):
            return deny_admin()
        try:
            item = service_of(request).toggle_item(item_id)
        except CardapioError as exc:
            return HTMLResponse(error_page("Item", exc.message), status_code=exc.status_code)
        return RedirectResponse(f"/admin/restaurantes/{item.restaurant_id}", status_code=303)

    @app.post("/admin/restaurantes/{restaurant_id}/confirmar-pix")
    def confirm_pix(restaurant_id: int, request: Request) -> Response:
        return _plan_action(request, restaurant_id, "confirm")

    @app.post("/admin/restaurantes/{restaurant_id}/pausar")
    def pause_restaurant(restaurant_id: int, request: Request) -> Response:
        return _plan_action(request, restaurant_id, "pause")

    @app.post("/admin/restaurantes/{restaurant_id}/retomar")
    def resume_restaurant(restaurant_id: int, request: Request) -> Response:
        return _plan_action(request, restaurant_id, "resume")

    @app.post("/admin/pedidos/{order_id}/apagar")
    def delete_order(order_id: int, request: Request) -> Response:
        if not is_admin(request):
            return deny_admin()
        try:
            restaurant_id = service_of(request).delete_order(order_id)
        except CardapioError as exc:
            return HTMLResponse(error_page("Pedido", exc.message), status_code=exc.status_code)
        return RedirectResponse(f"/admin/restaurantes/{restaurant_id}", status_code=303)

    def _plan_action(request: Request, restaurant_id: int, action: str) -> Response:
        if not is_admin(request):
            return deny_admin()
        service = service_of(request)
        try:
            if action == "confirm":
                service.confirm_payment(restaurant_id)
            elif action == "pause":
                service.pause(restaurant_id)
            else:
                service.resume(restaurant_id)
        except CardapioError as exc:
            return _render_restaurant(request, restaurant_id, error=exc.message, status_code=exc.status_code)
        return RedirectResponse(f"/admin/restaurantes/{restaurant_id}", status_code=303)

    def _render_restaurant(
        request: Request,
        restaurant_id: int,
        *,
        error: str | None = None,
        status_code: int = 200,
    ) -> HTMLResponse:
        service = service_of(request)
        restaurant = service.repository.get_restaurant(restaurant_id)
        if restaurant is None:
            return HTMLResponse(error_page("Loja", "Loja não encontrada."), status_code=404)
        groups = service._groups(restaurant.id)
        orders = service.repository.list_orders(restaurant.id)
        settings = settings_of(request)
        page = restaurant_admin_page(
            restaurant,
            groups,
            orders,
            today=service.today(),
            menu_url=public_menu_url(settings.public_base, restaurant.slug),
            billing_link=service.billing_link(restaurant),
            pix_ready=bool(settings.pix_key),
            error=error,
        )
        return HTMLResponse(page, status_code=status_code)

    return app


async def read_form(request: Request) -> dict[str, str]:
    raw = (await request.body()).decode("utf-8")
    parsed = parse_qs(raw, keep_blank_values=True)
    return {key: values[0] if values else "" for key, values in parsed.items()}


def quantities_from_form(form: dict[str, str]) -> dict[int, int]:
    quantities: dict[int, int] = {}
    for key, value in form.items():
        if not key.startswith("qty_"):
            continue
        try:
            quantities[int(key[4:])] = int(value or "0")
        except ValueError as exc:
            raise CardapioError("Quantidade inválida.") from exc
    return quantities


app = create_app()
