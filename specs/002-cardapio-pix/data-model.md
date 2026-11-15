# Modelo de dados — Spec 002

SQLite em `CARDAPIO_DB_PATH` (padrão `data/cardapio.sqlite`).

## restaurants

| Campo | Tipo | Notas |
| --- | --- | --- |
| id | integer | chave |
| slug | text único | 3–40, minúsculas, números e hífen |
| name | text | |
| whatsapp | text | só dígitos, com DDI 55 |
| city | text | |
| category | text | ramo, por exemplo Marmitas |
| plan_status | text | `trial`, `active` ou `paused` |
| trial_ends_on | date | |
| paid_until | date nula | |
| monthly_price_cents | integer | |
| is_demo | integer | 1 só na loja `demo` |
| created_on | date | |

## categories

`id`, `restaurant_id`, `name`, `position`.

## items

`id`, `restaurant_id`, `category_id`, `name`, `description`, `price_cents`, `available`, `position`.

## orders

`id`, `restaurant_id`, `customer_name`, `customer_phone`, `note`, `total_cents`, `items_json`, `whatsapp_url`, `created_at`.

`items_json` é uma lista de `item_id`, `name`, `quantity`, `unit_price_cents`.

## leads

`id`, `name`, `whatsapp`, `business_name`, `city`, `created_at`.

Interesse vindo da página inicial. Não é uma loja ainda.
