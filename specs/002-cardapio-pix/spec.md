# Spec 002 — Cardápio Pix

Produto separado da API de filmes. Um operador (quem quer a renda extra) hospeda
um único processo e cobra mensalidade de pequenos negócios de comida.

## Por que este produto

- O cliente já existe: lanchonete, marmita, açaí e confeitaria que vendem pelo WhatsApp.
- Custo marginal perto de zero: SQLite, sem gateway, sem comissão sobre o pedido.
- A operação depois da venda é automática: o cardápio fica no ar, o pedido abre o WhatsApp e o cardápio pausa sozinho quando a mensalidade vence.
- A renda não é garantida. Ela só entra depois que um negócio aceita pagar. A meta realista é alguns clientes locais a R$ 39/mês, não renda passiva no primeiro dia.

## Atores

- **Operador**: dono desta instalação. Entra com um token, cadastra lojas e confirma Pix.
- **Loja**: negócio de comida que paga a mensalidade.
- **Cliente da loja**: pessoa que monta o pedido no celular. O pagamento da comida é combinado direto com a loja. Este sistema não recebe esse valor.

## Regras

1. Cada loja tem um link público `/r/{slug}`.
2. O cardápio fica aberto se não estiver pausado e se `paid_until` for hoje ou uma data futura, ou se o status for `trial` e `trial_ends_on` for hoje ou uma data futura.
3. Loja nova nasce em `trial` por 14 dias.
4. Confirmar o Pix soma 30 dias a partir da data mais tarde entre hoje, o fim do trial e o `paid_until` atual, e muda o status para `active`.
5. Pausar fecha o cardápio mesmo que ainda haja dias pagos. Retomar só funciona se o acesso ainda não venceu.
6. Pedido sem item, com quantidade inválida ou de item esgotado é recusado.
7. Pedido de cardápio fechado é recusado.
8. A loja de demonstração `demo` não entra na receita recorrente.
9. A receita recorrente é a soma das mensalidades das lojas `active`, abertas e que não são demonstração.
10. O painel lista quem precisa de cobrança: pausada, ou com acesso acabando em até 3 dias.
11. Nomes e telefones de pedidos ficam só no SQLite local. Esse arquivo não entra no Git.

## Aceite

- A página inicial explica o produto, mostra o preço padrão e o cardápio de exemplo, e guarda um interesse.
- O exemplo `demo` abre com itens e aceita um pedido que gera link `wa.me`.
- Cardápio vencido mostra pausa e não grava pedido.
- Sem o cookie do operador, o painel redireciona para o login.
- O operador cria loja, categoria e item, e o item aparece no cardápio público.
- Confirmar Pix aumenta a receita recorrente e empurra `paid_until`.
- Texto digitado pela loja é escapado no HTML.
- `GET /health` responde `ok` sem depender da API de filmes.
