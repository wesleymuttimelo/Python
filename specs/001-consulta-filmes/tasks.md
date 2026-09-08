# Tasks — Spec 001 Consulta de Filmes

Checklist de execução do `plan.md`. Marque com `[x]` ao concluir.

## T1 — Fundação do repositório

- [x] T1.1 Criar `.gitignore` (venv, env, cache, IDE)
- [x] T1.2 Criar `.env.example` com `OMDB_API_KEY=`
- [ ] T1.3 Criar `requirements.txt`
- [ ] T1.4 Criar estrutura de pastas `app/`, `tests/`

## T2 — Configuração e app base

- [ ] T2.1 Implementar `app/config.py` com Pydantic Settings
- [ ] T2.2 Implementar `app/main.py` com FastAPI
- [ ] T2.3 Implementar `GET /health`
- [ ] T2.4 Validar `uvicorn app.main:app --reload`

## T3 — Contratos internos

- [ ] T3.1 Criar schemas `MovieSummary`, `MovieDetail`, `MovieSearchResponse`
- [ ] T3.2 Criar schema `HealthStatus`
- [ ] T3.3 Conferir paridade com `contracts/openapi.yaml`

## T4 — Integração OMDb

- [ ] T4.1 Implementar `OmdbClient` com HTTPX async
- [ ] T4.2 Método de busca (`s=`)
- [ ] T4.3 Método de detalhe (`i=`)
- [ ] T4.4 Tratamento de timeout/erro de rede

## T5 — Serviços e rotas

- [ ] T5.1 Implementar `MovieService` + normalização `N/A`
- [ ] T5.2 Rota `GET /movies/search`
- [ ] T5.3 Rota `GET /movies/{imdb_id}`
- [ ] T5.4 Mapear 404 / 502 / 503 conforme spec

## T6 — Testes

- [ ] T6.1 Testes de health
- [ ] T6.2 Testes de search (sucesso, vazio, validação)
- [ ] T6.3 Testes de detail (sucesso, 404, validação)
- [ ] T6.4 Teste de key ausente → 503
- [ ] T6.5 `pytest -q` passando

## T7 — Encerramento didático

- [ ] T7.1 Exemplos `curl` no README
- [ ] T7.2 Percorrer `checklists/requirements.md`
- [ ] T7.3 Atualizar status da spec para `implementada`
