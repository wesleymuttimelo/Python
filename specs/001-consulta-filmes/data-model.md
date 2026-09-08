# Data Model — Consulta de Filmes

Modelos conceituais da nossa API (não o JSON bruto da OMDb).

## MovieSummary

Resultado de busca (item da lista).

| Campo | Tipo | Obrigatório | Origem OMDb | Notas |
|-------|------|-------------|-------------|-------|
| title | string | sim | `Title` | |
| year | string | sim | `Year` | Pode ser intervalo em alguns casos; manter string |
| imdb_id | string | sim | `imdbID` | Ex.: `tt0133093` |
| type | string | sim | `Type` | Normalmente `movie` |
| poster_url | string \| null | não | `Poster` | `null` se ausente ou `"N/A"` |

## MovieDetail

Detalhe completo.

| Campo | Tipo | Obrigatório | Origem OMDb | Notas |
|-------|------|-------------|-------------|-------|
| title | string | sim | `Title` | |
| year | string | sim | `Year` | |
| imdb_id | string | sim | `imdbID` | |
| type | string | sim | `Type` | |
| poster_url | string \| null | não | `Poster` | |
| rated | string \| null | não | `Rated` | |
| released | string \| null | não | `Released` | |
| runtime | string \| null | não | `Runtime` | |
| genre | string \| null | não | `Genre` | |
| director | string \| null | não | `Director` | |
| writers | string \| null | não | `Writer` | |
| actors | string \| null | não | `Actors` | |
| plot | string \| null | não | `Plot` | |
| language | string \| null | não | `Language` | |
| country | string \| null | não | `Country` | |
| awards | string \| null | não | `Awards` | |
| imdb_rating | string \| null | não | `imdbRating` | Manter string na v1 |
| imdb_votes | string \| null | não | `imdbVotes` | |

## HealthStatus

| Campo | Tipo | Valor |
|-------|------|-------|
| status | string | `"ok"` |

## Regras de normalização

1. Qualquer campo OMDb igual a `"N/A"` → `null` no nosso schema
2. Não expor a chave `apikey` em logs de request
3. Não repassar o JSON OMDb cru nas responses da v1 (sempre mapear)
