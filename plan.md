# Plan de Execução — Spec 001 (API de Consulta de Filmes)

Este plano transforma a spec `specs/001-consulta-filmes/spec.md` em implementação.
Siga a ordem das fases. Não pule a fase de setup de chave OMDb.

## Pré-requisitos

- Python 3.11+
- Conta/chave gratuita OMDb (ver `README.md`)
- Git

## Visão da arquitetura alvo

```text
Cliente HTTP
    │
    ▼
FastAPI (rotas) ──► Pydantic schemas
    │
    ▼
MovieService (regras + normalização)
    │
    ▼
OmdbClient (HTTPX) ──► https://www.omdbapi.com/
```

## Fase 0 — Preparação do ambiente

1. Criar ambiente virtual: `python -m venv .venv`
2. Ativar: `source .venv/bin/activate` (Linux/macOS)
3. Criar `requirements.txt` com:
   - `fastapi`
   - `uvicorn[standard]`
   - `httpx`
   - `pydantic-settings`
   - `python-dotenv`
   - `pytest`
   - `pytest-asyncio`
4. Instalar: `pip install -r requirements.txt`
5. Copiar `.env.example` → `.env` e preencher `OMDB_API_KEY`
6. Confirmar `.gitignore` com `.venv/`, `.env`, `__pycache__/`, `.pytest_cache/`

**Saída:** ambiente pronto e key carregável via settings.

## Fase 1 — Esqueleto FastAPI

1. Criar pacote `app/`
2. `app/config.py` — `BaseSettings` com:
   - `omdb_api_key: str`
   - `omdb_base_url: str = "https://www.omdbapi.com/"`
   - `omdb_timeout_seconds: float = 10.0`
   - `app_name: str = "Movie Consultation API"`
3. `app/main.py` — instanciar `FastAPI`, incluir routers, endpoint `/health`
4. Subir: `uvicorn app.main:app --reload`
5. Validar `/health` e `/docs`

**Saída:** API sobe e health check passa.

## Fase 2 — Schemas e contrato

1. Criar `app/schemas/movies.py` conforme `data-model.md`
2. Garantir alinhamento com `contracts/openapi.yaml`
3. Schema de resposta de busca: `MovieSearchResponse(query, results)`

**Saída:** modelos Pydantic prontos para as rotas.

## Fase 3 — Cliente OMDb

1. Criar `app/clients/omdb.py`
2. Métodos async:
   - `search_movies(query: str) -> dict`
   - `get_movie_by_imdb_id(imdb_id: str) -> dict`
3. Usar `httpx.AsyncClient` com timeout das settings
4. Tratar erros de rede → exceção de domínio mapeável para 502
5. Nunca logar a API key

**Saída:** integração isolada e testável.

## Fase 4 — Service layer

1. Criar `app/services/movies.py`
2. Mapear payload OMDb → schemas internos
3. Normalizar `"N/A"` → `None`
4. Regras:
   - busca sem resultados → lista vazia
   - detalhe com erro OMDb "Movie not found!" → 404
   - key ausente → 503

**Saída:** regras de negócio fora das rotas.

## Fase 5 — Rotas

1. `app/api/routes/health.py` → `GET /health`
2. `app/api/routes/movies.py`:
   - `GET /movies/search?q=`
   - `GET /movies/{imdb_id}`
3. Validar `imdb_id` com pattern `^tt\d+$`
4. Registrar routers em `main.py`

**Saída:** US-01, US-02 e US-03 atendidas.

## Fase 6 — Testes

1. Criar `tests/` com fixtures que mockam `OmdbClient`
2. Cobrir:
   - health 200
   - search sucesso / vazio / q inválido
   - detail sucesso / 404 / id inválido
   - ausência de key → 503
3. Rodar: `pytest -q`

**Saída:** checklist `checklists/requirements.md` majoritariamente marcada.

## Fase 7 — Documentação final

1. Revisar `README.md` (setup, key OMDb, exemplos curl)
2. Marcar tasks concluídas em `tasks.md`
3. Atualizar status da spec para `implementada` quando tudo passar

## Ordem de prioridade se o tempo for curto

1. Health + settings + README da key
2. Search
3. Detail
4. Testes
5. Polish de erros/timeout

## Definição de pronto deste plan

- Todas as tasks em `specs/001-consulta-filmes/tasks.md` concluídas
- Checklist de requirements sem itens críticos abertos
- `pytest` verde
- Demonstração manual via `/docs` ou `curl` com key real
