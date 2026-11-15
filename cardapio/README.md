# Cardápio Pix

Cardápio digital para lanchonete, marmita, açaí e confeitaria. O cliente monta o
pedido no celular e a conversa abre no WhatsApp da loja. Você cobra uma
mensalidade fixa por Pix. Não há taxa de gateway e o sistema não fica no meio
do pagamento da comida.

A renda não é automática no primeiro dia. Ela entra quando uma loja aceita
pagar. Depois disso, o cardápio fica no ar sozinho e pausa quando a mensalidade
vence.

## Conta realista

| | |
| --- | --- |
| Preço sugerido | R$ 39 por loja / mês |
| 8 lojas pagantes | R$ 312 / mês, antes de imposto |
| Custo de software | R$ 0 de API e R$ 0 de comissão |
| Hospedagem | a máquina que você já usa, ou um VPS pequeno |

Se isso virar renda recorrente, formalize como MEI. O software não substitui essa obrigação.

## Subir localmente

Na raiz do repositório, com o ambiente da API de filmes já instalado:

```bash
pip install -r requirements.txt
export CARDAPIO_ADMIN_TOKEN="troque-este-token"
export CARDAPIO_PIX_KEY="sua-chave-pix"
export CARDAPIO_PIX_NAME="Seu Nome"
export CARDAPIO_PUBLIC_BASE_URL="http://127.0.0.1:8001"
uvicorn cardapio.main:app --reload --port 8001
```

- Oferta: http://127.0.0.1:8001
- Exemplo: http://127.0.0.1:8001/r/demo
- Painel: http://127.0.0.1:8001/admin

O banco fica em `data/cardapio.sqlite` e não entra no Git. Ele guarda nome e
telefone de quem pediu. Não publique esse arquivo. Apague o pedido no painel
se a pessoa pedir.

## Rotina de venda

1. Escolha negócios que já vendem pelo WhatsApp e ainda usam cardápio em papel ou foto.
2. Cadastre a loja no painel e monte os itens na frente da pessoa.
3. Imprima o QR e deixe no balcão. O teste dura 14 dias.
4. Quando a lista "Cobrar agora" mostrar a loja, mande a mensagem pronta.
5. Confira o Pix na sua conta e só então aperte **Confirmar Pix de 30 dias**.
6. Quem não paga fica com o cardápio pausado, sem você tirar nada do ar na mão.

## Vender pelo anúncio

O anúncio não dispara mensagem para quem não pediu. A pessoa clica, cai na
página e o cardápio de teste abre sozinho. O editor privado fica em `/loja/...`.
O link público, esse sim, pode ir para o QR do balcão.

No painel, abra **Divulgar**. Lá estão os textos e os links prontos:

- `/?utm_source=instagram` para Instagram e Facebook
- `/?utm_source=google` para anúncio de pesquisa
- `/?utm_source=whatsapp` para status e grupos da sua cidade
- `/?utm_source=panfleto` para o QR impresso

Use o endereço público de verdade em `CARDAPIO_PUBLIC_BASE_URL`. `localhost` não
serve para anúncio.

Um teste honesto é cerca de R$ 15 por dia, por uma semana, só na sua cidade.
Se o cadastro custar mais que a mensalidade, pause o anúncio e volte para o
panfleto. Não compre lista de telefone.

## Publicar

Qualquer máquina com Python 3.11+ serve. Aponte `CARDAPIO_PUBLIC_BASE_URL` para
o endereço real, com `https://` se houver certificado, e use um token longo.
Não reutilize o token de exemplo.

```bash
CARDAPIO_COOKIE_SECURE=true uvicorn cardapio.main:app --host 0.0.0.0 --port 8001
```

`CARDAPIO_COOKIE_SECURE=true` só funciona atrás de HTTPS.
