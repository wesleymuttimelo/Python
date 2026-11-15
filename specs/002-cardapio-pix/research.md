# Pesquisa — Spec 002

## Alternativas descartadas

| Ideia | Por que não |
| --- | --- |
| Bot de investimento ou arbitragem | Promete dinheiro fácil e pode virar prejuízo. Fora de escopo. |
| Site de anúncios ou afiliados | Custo baixo, mas o dinheiro depende de tráfego que um projeto novo não tem. |
| Agregador de vagas por scraping | APIs públicas existem, porém a renda é indireta e o conteúdo some sem audiência. |
| Gateway no meio do pedido da comida | Taxa, KYC e risco de virar intermediador de pagamento. Desnecessário. |

## Decisão

Cardápio com pedido no WhatsApp e mensalidade por Pix manual.

- WhatsApp já é o caixa de muitos negócios pequenos no Brasil.
- O Pix da mensalidade é conferido pelo operador. Não há tarifa de intermediário.
- A pausa automática é o que torna a cobrança repetível sem um banco no meio.
- O preço sugerido é R$ 39/mês. Com 8 lojas ativas, a receita bruta é R$ 312/mês. Hospedagem pode ser a máquina que já está ligada, ou um VPS barato.
- Quando a renda for recorrente, o caminho formal é o MEI. Isso é uma obrigação do operador, não uma função do software.

## O que fica manual de propósito

Confirmar que o Pix caiu. Consultar extrato via API de banco custa integração e credencial. O painel gera a mensagem pronta; o operador confere o Pix e aperta um botão.
