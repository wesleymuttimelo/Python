from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from cardapio.config import CardapioSettings
from cardapio.main import create_app
from cardapio.service import CardapioService


@pytest.fixture
def cardapio_app(tmp_path):
    settings = CardapioSettings(
        admin_token="test-admin-token",
        db_path=str(tmp_path / "cardapio.sqlite"),
        public_base_url="http://testserver",
        pix_key="teste@pix",
        pix_name="Ana Operadora",
        trial_days=14,
        default_price_cents=3900,
    )
    return create_app(settings)


@pytest.fixture
def client(cardapio_app):
    with TestClient(cardapio_app) as test_client:
        yield test_client


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "cardapio-pix"}


def test_landing_links_demo_and_price(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "R$ 39,00" in response.text
    assert "/r/demo" in response.text
    assert "garantida" not in response.text.lower()


def test_demo_menu_and_order_opens_whatsapp(client):
    menu = client.get("/api/cardapio/demo")
    assert menu.status_code == 200
    payload = menu.json()
    assert payload["is_open"] is True
    item_id = payload["categories"][0]["items"][0]["id"]

    page = client.get("/r/demo")
    assert "Frango grelhado" in page.text

    created = client.post(
        "/r/demo/pedidos",
        data={
            "customer_name": "Joana",
            "customer_phone": "11977776666",
            f"qty_{item_id}": "2",
            "note": "sem cebola",
        },
        follow_redirects=False,
    )
    assert created.status_code == 303
    confirmation = client.get(created.headers["location"])
    assert confirmation.status_code == 200
    assert "https://wa.me/5511999990000?text=" in confirmation.text
    assert "R$ 44,00" in confirmation.text


def test_empty_order_is_rejected(client):
    response = client.post(
        "/r/demo/pedidos",
        data={"customer_name": "Joana", "customer_phone": "11977776666", "note": ""},
    )
    assert response.status_code == 400
    assert "pelo menos um item" in response.text


def test_expired_trial_blocks_orders(client, cardapio_app):
    service: CardapioService = cardapio_app.state.service
    restaurant = service.create_restaurant(
        name="Bolo da Lia",
        whatsapp="11966665555",
        city="Santos",
        category="Bolos",
        slug="bolo-da-lia",
    )
    category = service.add_category(restaurant.id, "Bolos")
    item = service.add_item(
        restaurant.id,
        category_id=category.id,
        name="Fatia",
        description="",
        price="10,00",
    )
    service.repository.set_trial_end(
        restaurant.id,
        service.today() - timedelta(days=1),
        "trial",
    )

    page = client.get("/r/bolo-da-lia")
    assert page.status_code == 200
    assert "pausado" in page.text
    denied = client.post(
        "/r/bolo-da-lia/pedidos",
        data={
            "customer_name": "Joana",
            "customer_phone": "11977776666",
            f"qty_{item.id}": "1",
        },
    )
    assert denied.status_code == 403
    assert service.repository.list_orders(restaurant.id) == []


def test_admin_requires_token_and_can_publish_a_menu(client):
    assert client.get("/admin", follow_redirects=False).status_code == 303

    login = client.post(
        "/admin/login",
        data={"token": "test-admin-token"},
        follow_redirects=False,
    )
    assert login.status_code == 303

    created = client.post(
        "/admin/restaurantes",
        data={
            "name": "Açaí do Zé",
            "whatsapp": "11988887777",
            "city": "Campinas",
            "category": "Açaí",
            "slug": "acai-do-ze",
            "monthly_price": "39,00",
        },
        follow_redirects=False,
    )
    assert created.status_code == 303
    admin_page = client.get(created.headers["location"])
    assert "Açaí do Zé" in admin_page.text

    restaurant_id = created.headers["location"].rstrip("/").split("/")[-1]
    category = client.post(
        f"/admin/restaurantes/{restaurant_id}/categorias",
        data={"name": "Tigelas"},
        follow_redirects=False,
    )
    assert category.status_code == 303
    admin_page = client.get(category.headers["location"])
    category_id = admin_page.text.split('name="category_id"')[1]
    option = category_id.split('value="', 1)[1].split('"', 1)[0]

    item = client.post(
        f"/admin/restaurantes/{restaurant_id}/itens",
        data={
            "category_id": option,
            "name": "<script>alert(1)</script>",
            "description": "com granola",
            "price": "18,00",
        },
        follow_redirects=False,
    )
    assert item.status_code == 303

    public = client.get("/r/acai-do-ze")
    assert public.status_code == 200
    assert "<script>alert(1)</script>" not in public.text
    assert "&lt;script&gt;" in public.text
    assert "R$ 18,00" in public.text


def test_confirming_pix_counts_recurring_revenue(client):
    client.post("/admin/login", data={"token": "test-admin-token"}, follow_redirects=False)
    created = client.post(
        "/admin/restaurantes",
        data={
            "name": "Pastel da Rua",
            "whatsapp": "21999998888",
            "city": "Rio de Janeiro",
            "category": "Pastel",
            "slug": "pastel-da-rua",
            "monthly_price": "39,00",
        },
        follow_redirects=False,
    )
    restaurant_path = created.headers["location"]
    before = client.get("/admin")
    assert 'id="mrr">R$ 0,00' in before.text

    confirmed = client.post(f"{restaurant_path}/confirmar-pix", follow_redirects=False)
    assert confirmed.status_code == 303
    after = client.get("/admin")
    assert 'id="mrr">R$ 39,00' in after.text


def test_lead_form_reaches_the_dashboard(client):
    response = client.post(
        "/interessados",
        data={
            "name": "Marina",
            "whatsapp": "11955554444",
            "business_name": "Doces da Marina",
            "city": "Osasco",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    client.post("/admin/login", data={"token": "test-admin-token"})
    dashboard = client.get("/admin")
    assert "Doces da Marina" in dashboard.text


def test_qr_svg_and_print_page(client):
    printed = client.get("/r/demo/imprimir")
    assert printed.status_code == 200
    assert "http://testserver/r/demo" in printed.text
    response = client.get("/r/demo/qr.svg")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/svg+xml")
    assert b"<svg" in response.content


def test_unknown_menu_is_not_found(client):
    response = client.get("/api/cardapio/nao-existe")
    assert response.status_code == 404
