# Tasks — Spec 001 Consulta de Filmes

Checklist de execução do `plan.md`. Marque com `[x]` ao concluir.

## T1 — Fundação do repositório

- [x] T1.1 Criar `.gitignore` (venv, env, cache, IDE)
- [x] T1.2 Criar `.env.example` com `OMDB_API_KEY=`
- [x] T1.3 Criar `requirements.txt`
- [x] T1.4 Criar estrutura de pastas `app/`, `tests/`

## T2 — Configuração e app base

- [x] T2.1 Implementar `app/config.py` com Pydantic Settings
- [x] T2.2 Implementar `app/main.py` com FastAPI
- [x] T2.3 Implementar `GET /health`
- [x] T2.4 Validar `uvicorn app.main:app --reload`

## T3 — Contratos internos

- [x] T3.1 Criar schemas `MovieSummary`, `MovieDetail`, `MovieSearchResponse`
- [x] T3.2 Criar schema `HealthStatus`
- [x] T3.3 Conferir paridade com `contracts/openapi.yaml`

## T4 — Integração OMDb

- [x] T4.1 Implementar `OmdbClient` com HTTPX async
- [x] T4.2 Método de busca (`s=`)
- [x] T4.3 Método de detalhe (`i=`)
- [x] T4.4 Tratamento de timeout/erro de rede

## T5 — Serviços e rotas

- [x] T5.1 Implementar `MovieService` + normalização `N/A`
- [x] T5.2 Rota `GET /movies/search`
- [x] T5.3 Rota `GET /movies/{imdb_id}`
- [x] T5.4 Mapear 404 / 502 / 503 conforme spec

## T6 — Testes

- [x] T6.1 Testes de health
- [x] T6.2 Testes de search (sucesso, vazio, validação)
- [x] T6.3 Testes de detail (sucesso, 404, validação)
- [x] T6.4 Teste de key ausente → 503
- [x] T6.5 `pytest -q` passando

## T7 — Encerramento didático

- [x] T7.1 Exemplos `curl` no README
- [x] T7.2 Percorrer `checklists/requirements.md`
- [x] T7.3 Atualizar status da spec para `implementada`
