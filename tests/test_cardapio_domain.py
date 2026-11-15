from datetime import date, timedelta

from cardapio.domain import (
    CardapioError,
    Restaurant,
    build_whatsapp_url,
    counts_as_mrr,
    extend_paid_until,
    format_brl,
    menu_is_open,
    needs_billing,
    normalize_whatsapp,
    parse_price_to_cents,
    slugify,
)


def sample_restaurant(**overrides) -> Restaurant:
    data = {
        "id": 1,
        "slug": "ana",
        "name": "Ana",
        "whatsapp": "5511999998888",
        "city": "São Paulo",
        "category": "Marmitas",
        "plan_status": "trial",
        "trial_ends_on": date(2026, 11, 20),
        "paid_until": None,
        "monthly_price_cents": 3900,
        "is_demo": False,
        "created_on": date(2026, 11, 1),
    }
    data.update(overrides)
    return Restaurant(**data)


def test_slugify_strips_accents_and_spaces():
    assert slugify("Açaí do Zé") == "acai-do-ze"


def test_format_and_parse_brazilian_price():
    assert format_brl(3900) == "R$ 39,00"
    assert parse_price_to_cents("39,00") == 3900
    assert parse_price_to_cents("R$ 1.234,50") == 123450


def test_parse_price_rejects_garbage():
    try:
        parse_price_to_cents("caro")
    except CardapioError as exc:
        assert exc.status_code == 400
    else:
        raise AssertionError("preço inválido deveria falhar")


def test_whatsapp_adds_brazil_code():
    assert normalize_whatsapp("(11) 98888-7777") == "5511988887777"
    url = build_whatsapp_url("5511988887777", "Olá")
    assert url.startswith("https://wa.me/5511988887777?text=")


def test_trial_is_open_until_the_last_day():
    today = date(2026, 11, 20)
    restaurant = sample_restaurant()
    assert menu_is_open(restaurant, today) is True
    assert menu_is_open(restaurant, today + timedelta(days=1)) is False


def test_pause_closes_even_with_credit():
    restaurant = sample_restaurant(plan_status="paused", paid_until=date(2026, 12, 1))
    assert menu_is_open(restaurant, date(2026, 11, 15)) is False


def test_payment_extends_from_the_later_date():
    restaurant = sample_restaurant()
    assert extend_paid_until(restaurant, date(2026, 11, 15)) == date(2026, 12, 20)


def test_expired_payment_extends_from_today():
    restaurant = sample_restaurant(
        plan_status="active",
        paid_until=date(2026, 11, 10),
        trial_ends_on=date(2026, 11, 1),
    )
    assert extend_paid_until(restaurant, date(2026, 11, 15)) == date(2026, 12, 15)


def test_billing_window_and_mrr_ignore_demo_and_trial():
    today = date(2026, 11, 15)
    trial = sample_restaurant()
    demo = sample_restaurant(is_demo=True, plan_status="active", paid_until=date(2026, 12, 1))
    active = sample_restaurant(plan_status="active", paid_until=date(2026, 11, 16))
    assert needs_billing(trial, today) is False
    assert needs_billing(active, today) is True
    assert needs_billing(demo, today) is False
    assert counts_as_mrr(active, today) is True
    assert counts_as_mrr(trial, today) is False
    assert counts_as_mrr(demo, today) is False
