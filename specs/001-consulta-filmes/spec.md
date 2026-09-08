# Spec 001 — API de Consulta de Filmes

**Status:** implementada  
**Objetivo de estudo:** Python + FastAPI + integração HTTP com API externa  
**Provedor externo:** [OMDb API](https://www.omdbapi.com/) (Open Movie Database)

## Resumo

Construir uma API REST com FastAPI que permite buscar filmes e obter detalhes,
consultando a OMDb por trás de uma camada de serviço própria.

A API deste projeto é um **BFF/wrapper didático**: o cliente final fala com
nossa FastAPI; nossa FastAPI fala com a OMDb.

## Motivação

- Aprender estrutura de projeto FastAPI
- Praticar settings, schemas (Pydantic), rotas e testes
- Integrar com um serviço gratuito real (requer API key)

## Personas

| Persona | Necessidade |
|---------|-------------|
| Estudante | Rodar localmente, ler o código e entender cada camada |
| Cliente HTTP | Buscar filmes por título e ver detalhes por ID IMDb |

## User Stories

### US-01 — Health check

**Como** desenvolvedor,  
**quero** um endpoint de saúde,  
**para** validar que a API sobe corretamente.

**Aceite:**

- `GET /health` retorna `200` com `{"status": "ok"}`

### US-02 — Buscar filmes por título

**Como** cliente da API,  
**quero** buscar filmes pelo título (ou parte dele),  
**para** encontrar candidatos rapidamente.

**Aceite:**

- `GET /movies/search?q={termo}` é obrigatório (`q` não vazio)
- Retorna lista tipada (título, ano, imdb_id, tipo, poster quando disponível)
- Se a OMDb não encontrar resultados, retorna lista vazia `[]` com `200`
- Se `q` estiver ausente/vazio, retorna `422`
- Se a API key estiver ausente/inválida no servidor, retorna `503` com mensagem clara

### US-03 — Detalhes de um filme

**Como** cliente da API,  
**quero** consultar detalhes por `imdb_id`,  
**para** ver sinopse, elenco, notas e metadados.

**Aceite:**

- `GET /movies/{imdb_id}` retorna detalhes normalizados
- `imdb_id` deve parecer ID IMDb (`tt` + dígitos); caso inválido → `422`
- Filme inexistente → `404`
- API key inválida/ausente → `503`

### US-04 — Documentação interativa

**Como** estudante,  
**quero** abrir o Swagger/OpenAPI do FastAPI,  
**para** explorar e testar endpoints sem cliente externo.

**Aceite:**

- `/docs` e `/openapi.json` disponíveis em modo desenvolvimento

## Fora de escopo (v1)

- Autenticação de usuários
- Banco de dados / persistência
- Cache Redis
- Rate limiting avançado
- Deploy em nuvem
- Endpoints de séries além do que a busca OMDb já devolver incidentalmente
- Frontend

## Requisitos não funcionais

| ID | Requisito |
|----|-----------|
| NFR-01 | Python 3.11+ |
| NFR-02 | Dependências mínimas: FastAPI, Uvicorn, HTTPX, Pydantic Settings, python-dotenv |
| NFR-03 | Configuração via variáveis de ambiente |
| NFR-04 | Testes com mock do cliente OMDb (sem rede obrigatória no CI local) |
| NFR-05 | Código em inglês; documentação SDD em português |
| NFR-06 | Tempo de resposta da nossa API depende da OMDb; timeout configurável (padrão 10s) |

## Modelo de erros (v1)

| Situação | HTTP | Corpo (exemplo) |
|----------|------|-----------------|
| Validação de query/path | 422 | detalhe padrão FastAPI/Pydantic |
| Filme não encontrado | 404 | `{"detail": "Filme não encontrado"}` |
| Falha de configuração/provedor | 503 | `{"detail": "Serviço de filmes indisponível"}` |
| Timeout/erro de rede com OMDb | 502 | `{"detail": "Falha ao consultar o provedor de filmes"}` |

## Critérios de pronto da feature

- [x] Spec, plan, tasks e contrato revisados
- [x] App FastAPI sobe com `uvicorn`
- [x] Endpoints US-01..US-03 implementados
- [x] Testes passando com mocks
- [x] README explica chave OMDb e como rodar
- [x] `.env.example` presente; `.env` no `.gitignore`
