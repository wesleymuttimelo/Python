# Specs

Cada pasta `NNN-nome` é uma feature especificada antes da implementação.

## Convenção

```text
specs/
  NNN-nome-da-feature/
    spec.md          # requisitos e aceite
    research.md      # decisões e alternativas
    data-model.md    # entidades
    tasks.md         # checklist de implementação
    contracts/       # OpenAPI e outros contratos
    checklists/      # validação de pronto
```

## Features

| ID | Nome | Status |
|----|------|--------|
| 001 | Consulta de filmes (OMDb + FastAPI) | Especificada — pronta para execução via `plan.md` |

## Como criar uma nova spec

1. Copie a estrutura de `001-consulta-filmes/`
2. Incremente o número (`002-...`)
3. Atualize `plan.md` na raiz se a execução mudar
4. Só implemente depois de tasks claras
