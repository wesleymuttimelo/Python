# Checklist de requisitos — Spec 001

Use este checklist para validar se a implementação cumpriu a spec.

## Funcional

- [ ] `GET /health` → 200 `{"status":"ok"}`
- [ ] `GET /movies/search?q=matrix` → 200 com `query` e `results`
- [ ] `GET /movies/search` (sem q) → 422
- [ ] `GET /movies/search?q=` → 422
- [ ] Busca sem resultados → 200 com `results: []`
- [ ] `GET /movies/tt0133093` → 200 com detalhes
- [ ] `GET /movies/abc` → 422
- [ ] `GET /movies/tt0000000` (inexistente) → 404
- [ ] Sem `OMDB_API_KEY` → endpoints de filmes respondem 503

## Qualidade

- [ ] Cliente OMDb isolado em módulo próprio
- [ ] Schemas Pydantic alinhados ao data-model
- [ ] Testes unitários/integration com mock (sem rede)
- [ ] `.env` ignorado pelo Git
- [ ] README com passo a passo da chave OMDb
- [ ] `/docs` abre a documentação Swagger
