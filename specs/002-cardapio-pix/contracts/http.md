# Contrato HTTP — Spec 002

App próprio: `uvicorn cardapio.main:app --port 8001`.
Não divide porta nem rotas com a API de filmes.

## Público

| Método | Caminho | Resposta |
| --- | --- | --- |
| GET | `/health` | `200 {"status":"ok","service":"cardapio-pix"}` |
| GET | `/` | HTML da oferta |
| POST | `/interessados` | `303 /obrigado` ou `400` HTML |
| GET | `/r/{slug}` | HTML do cardápio, ou pausa se estiver fechado |
| POST | `/r/{slug}/pedidos` | `303` para o pedido criado, `400` ou `403` HTML |
| GET | `/r/{slug}/pedidos/{id}` | HTML com link `https://wa.me/` |
| GET | `/r/{slug}/imprimir` | HTML para impressão |
| GET | `/r/{slug}/qr.svg` | `image/svg+xml` |
| GET | `/api/cardapio/{slug}` | JSON do cardápio e `is_open` |

Pedido JSON não existe. O formulário HTML usa `application/x-www-form-urlencoded` com campos `customer_name`, `customer_phone`, `note` e `qty_{item_id}`.

`GET /api/cardapio/{slug}`:

```json
{
  "slug": "demo",
  "name": "Marmitas da Ana",
  "is_open": true,
  "categories": [
    {
      "name": "Marmitas",
      "items": [
        {"id": 1, "name": "Frango grelhado", "price_cents": 2200, "available": true}
      ]
    }
  ]
}
```

Slug desconhecido: `404` com `{"detail":"Cardápio não encontrado."}`.

## Operador

Cookie `cardapio_admin` com o valor de `CARDAPIO_ADMIN_TOKEN`. Sem cookie, as rotas `/admin` respondem `303 /admin/login`.

| Método | Caminho | Efeito |
| --- | --- | --- |
| POST | `/admin/login` | grava o cookie se o token coincidir |
| POST | `/admin/sair` | apaga o cookie |
| GET | `/admin` | painel |
| POST | `/admin/restaurantes` | cria loja em trial |
| POST | `/admin/restaurantes/{id}/categorias` | nova categoria |
| POST | `/admin/restaurantes/{id}/itens` | novo item |
| POST | `/admin/itens/{id}/disponibilidade` | alterna esgotado |
| POST | `/admin/restaurantes/{id}/confirmar-pix` | estende 30 dias |
| POST | `/admin/restaurantes/{id}/pausar` | fecha o cardápio |
| POST | `/admin/restaurantes/{id}/retomar` | reabre se ainda houver acesso |
| POST | `/admin/pedidos/{id}/apagar` | remove o pedido |
