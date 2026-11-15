import html
from datetime import date

from cardapio.domain import (
    Category,
    Item,
    Order,
    Restaurant,
    format_brl,
    menu_is_open,
    public_menu_url,
)

BASE_CSS = """
:root {
  --paper: #f4efe4;
  --ink: #1c1915;
  --muted: #5e564c;
  --line: #ddd4c4;
  --green: #1f6b45;
  --green-dark: #144a30;
  --clay: #8a3b12;
  --card: #fffaf2;
  --warn: #8a2e24;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--paper);
  color: var(--ink);
  font-family: "Avenir Next", "Segoe UI", sans-serif;
  line-height: 1.45;
}
a { color: var(--green-dark); }
h1, h2, h3 { font-family: Georgia, "Iowan Old Style", serif; font-weight: 600; }
main { width: min(920px, calc(100% - 32px)); margin: 0 auto; padding: 28px 0 64px; }
.top {
  display: flex; justify-content: space-between; gap: 16px; align-items: center;
  padding: 18px 0; border-bottom: 1px solid var(--line); margin-bottom: 28px;
}
.brand { font-family: Georgia, serif; font-size: 1.25rem; text-decoration: none; color: inherit; }
.nav { display: flex; gap: 14px; align-items: center; }
.hero { display: grid; gap: 18px; }
.eyebrow { letter-spacing: .08em; text-transform: uppercase; font-size: .78rem; color: var(--muted); margin: 0; }
.lead { font-size: 1.15rem; max-width: 38rem; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; }
.card, form.card, .item {
  background: var(--card); border: 1px solid var(--line); border-radius: 16px; padding: 16px;
}
.price { color: var(--clay); font-size: 1.6rem; margin: 0; }
button, .button {
  display: inline-flex; align-items: center; justify-content: center;
  background: var(--green); color: white; border: 0; border-radius: 999px;
  padding: 12px 18px; font: inherit; text-decoration: none; cursor: pointer;
}
button.secondary, a.secondary { background: transparent; color: var(--ink); border: 1px solid var(--line); }
button.warn { background: var(--warn); }
label { display: block; font-size: .92rem; margin-bottom: 12px; }
input, textarea, select {
  width: 100%; margin-top: 6px; padding: 12px; border-radius: 12px;
  border: 1px solid var(--line); background: white; font: inherit;
}
.item { display: flex; justify-content: space-between; gap: 12px; align-items: center; }
.item input[type="number"] { width: 84px; }
.buy { text-align: right; }
.muted { color: var(--muted); }
.error { background: #fde8e4; border: 1px solid #e7b2a8; padding: 12px 14px; border-radius: 12px; }
.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; }
.stat strong { display: block; font-size: 1.4rem; }
table { width: 100%; border-collapse: collapse; }
th, td { text-align: left; padding: 8px 6px; border-bottom: 1px solid var(--line); vertical-align: top; }
.actions { display: flex; flex-wrap: wrap; gap: 8px; }
.print-sheet { text-align: center; padding-top: 48px; }
.print-sheet img { width: 240px; height: 240px; }
@media print {
  .no-print { display: none; }
  body { background: white; }
}
"""


def _e(value: object) -> str:
    return html.escape(str(value), quote=True)


def page(title: str, body: str, *, noindex: bool = False) -> str:
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{_e(title)}</title>
  {robots}
  <style>{BASE_CSS}</style>
</head>
<body>
  <main>
    {body}
  </main>
</body>
</html>"""


def landing_page(price_label: str, *, error: str | None = None) -> str:
    error_html = f'<p class="error">{_e(error)}</p>' if error else ""
    body = f"""
    <header class="top">
      <a class="brand" href="/">Cardápio Pix</a>
      <nav class="nav"><a href="/admin">Painel</a></nav>
    </header>
    <section class="hero">
      <p class="eyebrow">Para quem vende comida no WhatsApp</p>
      <h1>Cardápio no celular. O pedido cai no WhatsApp.</h1>
      <p class="lead">Lanchonete, marmita, açaí e confeitaria. Sem taxa por pedido. A mensalidade é um Pix de { _e(price_label) }.</p>
      <p class="actions">
        <a class="button" href="/r/demo">Ver cardápio de exemplo</a>
        <a class="button secondary" href="#testar">Testar 14 dias</a>
      </p>
    </section>
    <section class="grid" style="margin-top:28px">
      <article class="card"><h2>1. Monta</h2><p>Nome, preço e o que está esgotado. Dá para fazer no balcão, em poucos minutos.</p></article>
      <article class="card"><h2>2. Imprime</h2><p>Um QR code fica na mesa. O cliente escolhe a quantidade no próprio celular.</p></article>
      <article class="card"><h2>3. Recebe</h2><p>O pedido abre uma conversa pronta no WhatsApp da loja. A comida é paga direto com ela.</p></article>
    </section>
    <section class="card" id="testar" style="margin-top:22px">
      <h2>Quero testar 14 dias</h2>
      <p class="muted">Sem cartão. Se não pagar depois do teste, o cardápio pausa sozinho.</p>
      {error_html}
      <form method="post" action="/interessados">
        <label>Seu nome<input name="name" required maxlength="80"></label>
        <label>WhatsApp<input name="whatsapp" required inputmode="tel" placeholder="11999998888"></label>
        <label>Nome do negócio<input name="business_name" required maxlength="80"></label>
        <label>Cidade<input name="city" required maxlength="60"></label>
        <button type="submit">Pedir o teste</button>
      </form>
    </section>
    """
    return page("Cardápio Pix", body)


def thanks_page() -> str:
    body = """
    <header class="top"><a class="brand" href="/">Cardápio Pix</a></header>
    <h1>Recebemos seu interesse.</h1>
    <p>O operador desta instalação entra em contato pelo WhatsApp para montar o cardápio de teste.</p>
    <p><a class="button" href="/r/demo">Enquanto isso, veja o exemplo</a></p>
    """
    return page("Interesse recebido", body)


def login_page(*, error: str | None = None, token_missing: bool = False) -> str:
    notice = ""
    if token_missing:
        notice = "<p class=\"error\">Defina CARDAPIO_ADMIN_TOKEN antes de usar o painel.</p>"
    elif error:
        notice = f'<p class="error">{_e(error)}</p>'
    body = f"""
    <header class="top"><a class="brand" href="/">Cardápio Pix</a></header>
    <h1>Painel do operador</h1>
    {notice}
    <form class="card" method="post" action="/admin/login">
      <label>Token<input name="token" type="password" autocomplete="current-password" required></label>
      <button type="submit">Entrar</button>
    </form>
    """
    return page("Entrar", body, noindex=True)


def dashboard_page(data: dict, price_label: str, *, error: str | None = None) -> str:
    error_html = f'<p class="error">{_e(error)}</p>' if error else ""
    rows = []
    for restaurant in data["restaurants"]:
        rows.append(
            "<tr>"
            f"<td><a href=\"/admin/restaurantes/{restaurant.id}\">{_e(restaurant.name)}</a>"
            f"<div class=\"muted\">/{_e(restaurant.slug)}</div></td>"
            f"<td>{_e(restaurant.plan_status)}</td>"
            f"<td>{_e(format_brl(restaurant.monthly_price_cents))}</td>"
            "</tr>"
        )
    due_items = "".join(
        f"<li><a href=\"/admin/restaurantes/{restaurant.id}\">{_e(restaurant.name)}</a></li>"
        for restaurant in data["due"]
    ) or "<li>Nenhuma cobrança nesta janela.</li>"
    leads = "".join(
        "<li>"
        f"{_e(lead.business_name)} — {_e(lead.name)} — {_e(lead.whatsapp)} — {_e(lead.city)}"
        "</li>"
        for lead in data["leads"]
    ) or "<li>Nenhum interesse ainda.</li>"
    body = f"""
    {_admin_header()}
    <h1>Painel</h1>
    <section class="stats">
      <article class="card stat"><span class="muted">Receita recorrente</span><strong id="mrr">{_e(format_brl(data["mrr_cents"]))}</strong></article>
      <article class="card stat"><span class="muted">Cardápios abertos</span><strong>{data["open_count"]}</strong></article>
      <article class="card stat"><span class="muted">Pedidos no mês</span><strong>{data["orders_this_month"]}</strong></article>
    </section>
    <section class="grid" style="margin-top:18px">
      <article class="card">
        <h2>Cobrar agora</h2>
        <ul>{due_items}</ul>
      </article>
      <article class="card">
        <h2>Como conseguir os primeiros</h2>
        <ol>
          <li>Visite negócios que já vendem pelo WhatsApp e ainda usam foto ou papel.</li>
          <li>Monte o cardápio na frente da pessoa e deixe o QR no balcão.</li>
          <li>O teste dura 14 dias. A mensagem de Pix sai pronta na ficha da loja.</li>
          <li>Quem não paga fica pausado sozinho. Preço sugerido: {_e(price_label)}.</li>
        </ol>
      </article>
    </section>
    <h2>Lojas</h2>
    <table>
      <thead><tr><th>Nome</th><th>Plano</th><th>Mensalidade</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
    <h2>Nova loja</h2>
    {error_html}
    <form class="card" method="post" action="/admin/restaurantes">
      <label>Nome<input name="name" required maxlength="80"></label>
      <label>WhatsApp da loja<input name="whatsapp" required placeholder="11999998888"></label>
      <label>Cidade<input name="city" required></label>
      <label>Ramo<input name="category" required placeholder="Marmitas"></label>
      <label>Link, opcional<input name="slug" placeholder="marmitas-da-ana"></label>
      <label>Mensalidade<input name="monthly_price" placeholder="{_e(price_label)}"></label>
      <button type="submit">Criar teste de 14 dias</button>
    </form>
    <h2>Interesses da página</h2>
    <ul>{leads}</ul>
    """
    return page("Painel", body, noindex=True)


def restaurant_admin_page(
    restaurant: Restaurant,
    groups: list[tuple[Category, list[Item]]],
    orders: list[Order],
    *,
    today: date,
    menu_url: str,
    billing_link: str,
    pix_ready: bool,
    error: str | None = None,
) -> str:
    is_open = menu_is_open(restaurant, today)
    status = "aberto" if is_open else "fechado"
    error_html = f'<p class="error">{_e(error)}</p>' if error else ""
    category_options = "".join(
        f'<option value="{category.id}">{_e(category.name)}</option>'
        for category, _items in groups
    )
    if category_options:
        item_form = f"""
        <form class="card" method="post" action="/admin/restaurantes/{restaurant.id}/itens">
          <label>Categoria<select name="category_id" required>{category_options}</select></label>
          <label>Item<input name="name" required></label>
          <label>Descrição<textarea name="description" maxlength="200"></textarea></label>
          <label>Preço<input name="price" required placeholder="22,00"></label>
          <button type="submit">Adicionar item</button>
        </form>
        """
    else:
        item_form = "<p class=\"muted\">Crie uma categoria antes de adicionar itens.</p>"
    item_blocks = []
    for category, items in groups:
        rows = []
        for item in items:
            availability = "disponível" if item.available else "esgotado"
            rows.append(
                "<div class=\"item\">"
                f"<div><strong>{_e(item.name)}</strong>"
                f"<div class=\"muted\">{_e(item.description)} · {_e(availability)}</div></div>"
                f"<div class=\"buy\"><strong>{_e(format_brl(item.price_cents))}</strong>"
                f"<form method=\"post\" action=\"/admin/itens/{item.id}/disponibilidade\">"
                "<button class=\"secondary\" type=\"submit\">Alternar</button></form></div>"
                "</div>"
            )
        item_blocks.append(f"<h3>{_e(category.name)}</h3>" + "".join(rows))
    order_rows = []
    for order in orders:
        summary = ", ".join(f"{line.quantity}x {line.name}" for line in order.lines)
        order_rows.append(
            "<tr>"
            f"<td>{_e(order.customer_name)}<div class=\"muted\">{_e(summary)}</div></td>"
            f"<td>{_e(format_brl(order.total_cents))}</td>"
            f"<td><form method=\"post\" action=\"/admin/pedidos/{order.id}/apagar\">"
            "<button class=\"secondary\" type=\"submit\">Apagar</button></form></td>"
            "</tr>"
        )
    pix_note = "" if pix_ready else "<p class=\"error\">Configure CARDAPIO_PIX_KEY para a mensagem de cobrança sair completa.</p>"
    body = f"""
    {_admin_header()}
    <p class="eyebrow">{_e(restaurant.city)} · {_e(restaurant.category)} · {_e(status)}</p>
    <h1>{_e(restaurant.name)}</h1>
    <p class="actions">
      <a class="button" href="{_e(menu_url)}">Abrir cardápio</a>
      <a class="button secondary" href="/r/{_e(restaurant.slug)}/imprimir">Imprimir QR</a>
    </p>
    {error_html}
    <section class="card">
      <h2>Mensalidade { _e(format_brl(restaurant.monthly_price_cents)) }</h2>
      <p>Plano: {_e(restaurant.plan_status)}. Trial até {_e(restaurant.trial_ends_on.isoformat())}.
         Pago até {_e(restaurant.paid_until.isoformat() if restaurant.paid_until else "—")}.</p>
      {pix_note}
      <p class="actions">
        <a class="button" href="{_e(billing_link)}">Mandar cobrança no WhatsApp</a>
        <form method="post" action="/admin/restaurantes/{restaurant.id}/confirmar-pix">
          <button type="submit">Confirmar Pix de 30 dias</button>
        </form>
        <form method="post" action="/admin/restaurantes/{restaurant.id}/pausar">
          <button class="warn" type="submit">Pausar</button>
        </form>
        <form method="post" action="/admin/restaurantes/{restaurant.id}/retomar">
          <button class="secondary" type="submit">Retomar</button>
        </form>
      </p>
    </section>
    <h2>Cardápio</h2>
    {''.join(item_blocks) or '<p class="muted">Ainda não há categorias.</p>'}
    <form class="card" method="post" action="/admin/restaurantes/{restaurant.id}/categorias">
      <label>Nova categoria<input name="name" required></label>
      <button type="submit">Adicionar categoria</button>
    </form>
    {item_form}
    <h2>Pedidos recentes</h2>
    <table>{''.join(order_rows) or '<tr><td>Nenhum pedido ainda.</td></tr>'}</table>
    """
    return page(restaurant.name, body, noindex=True)


def public_menu_page(
    restaurant: Restaurant,
    groups: list[tuple[Category, list[Item]]],
    *,
    is_open: bool,
    error: str | None = None,
) -> str:
    if not is_open:
        body = f"""
        <header class="top"><a class="brand" href="/">Cardápio Pix</a></header>
        <p class="eyebrow">{_e(restaurant.city)}</p>
        <h1>{_e(restaurant.name)}</h1>
        <p class="error">Este cardápio está pausado. Fale direto com o estabelecimento.</p>
        """
        return page(restaurant.name, body)
    sections = []
    for category, items in groups:
        blocks = []
        for item in items:
            if item.available:
                control = (
                    f'<input type="number" name="qty_{item.id}" min="0" max="20" value="0" '
                    f'inputmode="numeric" aria-label="Quantidade de {_e(item.name)}">'
                )
            else:
                control = '<span class="muted">Esgotado</span>'
            description = f'<div class="muted">{_e(item.description)}</div>' if item.description else ""
            blocks.append(
                "<article class=\"item\">"
                f"<div><h3>{_e(item.name)}</h3>{description}</div>"
                f"<div class=\"buy\"><strong>{_e(format_brl(item.price_cents))}</strong>{control}</div>"
                "</article>"
            )
        sections.append(f"<h2>{_e(category.name)}</h2>" + "".join(blocks))
    error_html = f'<p class="error">{_e(error)}</p>' if error else ""
    body = f"""
    <header class="top">
      <div>
        <p class="eyebrow">{_e(restaurant.city)} · {_e(restaurant.category)}</p>
        <a class="brand" href="/r/{_e(restaurant.slug)}">{_e(restaurant.name)}</a>
      </div>
      <a class="no-print" href="/r/{_e(restaurant.slug)}/imprimir">QR</a>
    </header>
    <form method="post" action="/r/{_e(restaurant.slug)}/pedidos">
      {''.join(sections)}
      {error_html}
      <section class="card">
        <h2>Seus dados</h2>
        <label>Nome<input name="customer_name" required maxlength="80"></label>
        <label>WhatsApp<input name="customer_phone" required inputmode="tel" placeholder="11999998888"></label>
        <label>Observação<textarea name="note" maxlength="300"></textarea></label>
        <button type="submit">Enviar pedido no WhatsApp</button>
        <p class="muted">O pagamento da comida é combinado direto com a loja. Este sistema não recebe esse valor.</p>
      </section>
    </form>
    """
    return page(restaurant.name, body)


def order_page(restaurant: Restaurant, order: Order) -> str:
    lines = "".join(
        f"<li>{line.quantity}x {_e(line.name)} — {_e(format_brl(line.total_cents))}</li>"
        for line in order.lines
    )
    body = f"""
    <header class="top"><a class="brand" href="/r/{_e(restaurant.slug)}">{_e(restaurant.name)}</a></header>
    <h1>Pedido pronto</h1>
    <ul>{lines}</ul>
    <p class="price">{_e(format_brl(order.total_cents))}</p>
    <p>Abra a conversa no WhatsApp da loja para enviar o pedido.</p>
    <p><a class="button" href="{_e(order.whatsapp_url)}">Abrir WhatsApp</a></p>
    """
    return page("Pedido", body)


def print_page(restaurant: Restaurant, menu_url: str) -> str:
    body = f"""
    <article class="print-sheet">
      <p class="eyebrow no-print"><a href="/r/{_e(restaurant.slug)}">Voltar ao cardápio</a></p>
      <h1>{_e(restaurant.name)}</h1>
      <p>Aponte a câmera para ver o cardápio e pedir no WhatsApp.</p>
      <img src="/r/{_e(restaurant.slug)}/qr.svg" alt="QR code do cardápio de {_e(restaurant.name)}">
      <p>{_e(menu_url)}</p>
    </article>
    """
    return page(f"QR {restaurant.name}", body)


def error_page(title: str, message: str) -> str:
    body = f"""
    <header class="top"><a class="brand" href="/">Cardápio Pix</a></header>
    <h1>{_e(title)}</h1>
    <p class="error">{_e(message)}</p>
    """
    return page(title, body)


def _admin_header() -> str:
    return """
    <header class="top">
      <a class="brand" href="/admin">Cardápio Pix</a>
      <nav class="nav">
        <a href="/">Página de venda</a>
        <form method="post" action="/admin/sair"><button class="secondary" type="submit">Sair</button></form>
      </nav>
    </header>
    """


def menu_url_for(base_url: str, restaurant: Restaurant) -> str:
    return public_menu_url(base_url, restaurant.slug)
