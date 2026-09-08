# Checklist de requisitos — Spec 001

Use este checklist para validar se a implementação cumpriu a spec.

## Funcional

- [x] `GET /health` → 200 `{"status":"ok"}`
- [x] `GET /movies/search?q=matrix` → 200 com `query` e `results`
- [x] `GET /movies/search` (sem q) → 422
- [x] `GET /movies/search?q=` → 422
- [x] Busca sem resultados → 200 com `results: []`
- [x] `GET /movies/tt0133093` → 200 com detalhes
- [x] `GET /movies/abc` → 422
- [x] `GET /movies/tt0000000` (inexistente) → 404
- [x] Sem `OMDB_API_KEY` → endpoints de filmes respondem 503

## Qualidade

- [x] Cliente OMDb isolado em módulo próprio
- [x] Schemas Pydantic alinhados ao data-model
- [x] Testes unitários/integration com mock (sem rede)
- [x] `.env` ignorado pelo Git
- [x] README com passo a passo da chave OMDb
- [x] `/docs` abre a documentação Swagger
