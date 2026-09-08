# Guia para Agentes e Contribuidores (SDD)

Este projeto usa **Spec Driven Development (SDD)**.
Antes de escrever código, leia e siga este fluxo.

## Ordem de leitura

1. `constitution.md` — regras permanentes
2. `specs/001-consulta-filmes/spec.md` — o que construir
3. `plan.md` — como executar a spec
4. `specs/001-consulta-filmes/tasks.md` — checklist de implementação
5. `README.md` — setup local e chave OMDb

## Fluxo de trabalho

```text
Ideia → Spec → Plan → Tasks → Implementação → Testes → README atualizado
```

### Ao adicionar feature

1. Crie ou edite a pasta em `specs/NNN-nome-curto/`
2. Atualize `spec.md` com user stories e critérios de aceite
3. Atualize `plan.md` (raiz) ou o plan da feature, se necessário
4. Atualize `tasks.md` com tarefas marcáveis
5. Atualize o contrato em `contracts/` se a API pública mudar
6. Só então implemente o código FastAPI

### Ao corrigir bug

- Se o comportamento esperado já está na spec: corrija o código
- Se o comportamento esperado mudou: atualize a spec primeiro

## Estrutura esperada do código (após execução do plan)

```text
app/
  main.py
  config.py
  api/
    routes/
  services/
  schemas/
  clients/
tests/
```

## Não faça

- Implementar endpoints sem atualizar spec/contrato
- Commitar `.env` ou chaves da OMDb
- Misturar lógica HTTP da OMDb dentro das rotas FastAPI
- Expandir escopo (auth, DB, cache) sem nova spec
