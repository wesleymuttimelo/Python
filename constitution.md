# Constituição do Projeto

Princípios permanentes para o desenvolvimento desta API de consulta de filmes.
Qualquer spec, plan ou implementação deve respeitar estes princípios.

## Propósito

Este repositório existe para **estudo de Python com FastAPI**.
O código deve ser legível, didático e incremental — não um produto de produção complexo.

## Princípios

### I. Spec primeiro

Nenhuma funcionalidade nova começa no código.
Fluxo obrigatório:

1. Atualizar ou criar a **spec** em `specs/`
2. Revisar o **plan** de execução
3. Quebrar em **tasks**
4. Só então implementar

### II. Simplicidade didática

Prefira a solução mais simples que atenda à spec.
Evite over-engineering, padrões desnecessários e dependências extras.
Cada escolha técnica deve ser fácil de explicar em um estudo.

### III. Contrato explícito

A API pública é definida em contrato OpenAPI antes (ou junto) da implementação.
Mudanças de endpoint, query params ou response shape exigem atualização do contrato e da spec.

### IV. Segredos fora do código

Chaves de API e credenciais nunca entram no Git.
Use `.env` local e documente variáveis em `.env.example` e no `README.md`.

### V. Integração externa isolada

A OMDb (ou outro provedor) deve ficar atrás de um cliente/serviço dedicado.
Rotas FastAPI não devem montar URLs nem parsear JSON cru do provedor diretamente.

### VI. Testabilidade

Endpoints devem ser testáveis com mocks do provedor externo.
Testes cobrem o comportamento da nossa API, não a disponibilidade da OMDb.

### VII. Português na documentação, inglês no código

- Documentação (`specs/`, `plan.md`, `README.md`): português
- Código (módulos, funções, variáveis): inglês
- Mensagens de erro da API: português (público de estudo BR) ou inglês — escolher um e manter consistente (padrão deste projeto: **português**)

## Escopo fora da constituição

Autenticação de usuários, banco de dados persistente, cache distribuído e deploy em cloud **não** fazem parte do escopo inicial, salvo nova spec aprovada.
