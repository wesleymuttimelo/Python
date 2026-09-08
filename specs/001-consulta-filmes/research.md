# Research — Provedor de filmes

## Decisão

Usar a **OMDb API** (Open Movie Database) como provedor externo da v1.

## Alternativas consideradas

| Provedor | Prós | Contras | Decisão |
|----------|------|---------|---------|
| **OMDb** | Gratuita (1000 req/dia), setup rápido, API simples por query string | Dados baseados em IMDb; plano free limitado | **Escolhida** |
| TMDB | Rica, documentação excelente, imagens | Conta + app + token Bearer; um pouco mais verbosa para iniciantes | Reservada para v2/estudo avançado |
| TVMaze | Boa para séries, sem key em vários endpoints | Foco em TV, não em filmes | Fora do escopo |

## Por que OMDb serve bem ao estudo

1. Cadastro da key em minutos
2. Endpoints fáceis de entender (`s=` busca, `i=` detalhes)
3. Ideal para ensinar: settings, HTTPX async, mapeamento de DTO externo → schema interno

## Endpoints OMDb relevantes

Base: `https://www.omdbapi.com/`

- Busca: `GET /?apikey={KEY}&s={termo}&type=movie`
- Detalhe: `GET /?apikey={KEY}&i={imdb_id}&plot=full`

Respostas OMDb usam `Response: "True"|"False"` e, em erro, `Error: "..."`.

## Riscos

| Risco | Mitigação |
|-------|-----------|
| Key não ativada / e-mail atrasado | Documentar no README; retornar 503 claro |
| Limite diário 1000 | Suficiente para estudo; mocks nos testes |
| Schema OMDb com campos string (`"N/A"`) | Normalizar no service (`None` quando `"N/A"`) |

## Referências

- https://www.omdbapi.com/
- https://www.omdbapi.com/apikey.aspx
