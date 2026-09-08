# Movie Consultation API

API de estudo em **Python + FastAPI** para consulta de filmes, integrada à
[OMDb API](https://www.omdbapi.com/) (Open Movie Database).

Este repositório é conduzido por **Spec Driven Development (SDD)**:
a especificação vem antes do código.

## Estado atual

A **spec 001** está **implementada**. A API FastAPI cobre health, busca e
detalhe de filmes, com testes mockados da OMDb.

## Documentação SDD

| Arquivo | Função |
|---------|--------|
| `constitution.md` | Princípios permanentes do projeto |
| `AGENTS.md` | Como trabalhar neste repo (fluxo SDD) |
| `specs/001-consulta-filmes/spec.md` | O que construir (user stories e aceite) |
| `specs/001-consulta-filmes/research.md` | Por que OMDb |
| `specs/001-consulta-filmes/data-model.md` | Modelo de dados |
| `specs/001-consulta-filmes/contracts/openapi.yaml` | Contrato da API |
| `specs/001-consulta-filmes/tasks.md` | Checklist de implementação |
| `specs/001-consulta-filmes/checklists/requirements.md` | Validação pós-implementação |
| `plan.md` | Instruções de execução da spec |

## Como obter a chave gratuita da OMDb

A OMDb exige uma API key (plano free: **1.000 requisições/dia**).

1. Abra a página de API key: [https://www.omdbapi.com/apikey.aspx](https://www.omdbapi.com/apikey.aspx)
2. Selecione a opção **FREE!** (limite diário de 1.000)
3. Preencha:
   - e-mail
   - nome
   - descrição curta do uso (ex.: `Estudo de FastAPI — consulta de filmes`)
4. Envie o formulário
5. Abra o e-mail recebido da OMDb (verifique spam/lixo eletrônico)
6. Clique no **link de ativação** — a key só funciona depois de ativada
7. Guarde a key com segurança (não compartilhe em commits públicos)

> Dica: contas Yahoo/Outlook às vezes atrasam o e-mail. Se não chegar em ~1 hora,
> use outro e-mail ou contate o suporte indicado no site da OMDb.

### Teste rápido da key (opcional)

No navegador ou terminal, troque `SUA_CHAVE`:

```bash
curl "https://www.omdbapi.com/?apikey=SUA_CHAVE&t=Matrix"
```

Se retornar JSON com dados do filme, a key está ativa.

## Configuração local (após implementar o app)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edite .env e cole sua OMDB_API_KEY
uvicorn app.main:app --reload
```

Abra:

- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Exemplos de uso (alvo da spec)

```bash
curl "http://localhost:8000/health"
curl "http://localhost:8000/movies/search?q=matrix"
curl "http://localhost:8000/movies/tt0133093"
```

## Variáveis de ambiente

Veja `.env.example`:

- `OMDB_API_KEY` — obrigatória para busca/detalhe
- `OMDB_BASE_URL` — padrão `https://www.omdbapi.com/`
- `OMDB_TIMEOUT_SECONDS` — padrão `10`

## Fluxo de estudo recomendado

1. Ler `constitution.md` e `AGENTS.md`
2. Ler a spec completa
3. Seguir `plan.md` fase a fase
4. Ir marcando `tasks.md`
5. Validar com o checklist de requirements

## Licença / propósito

Material de estudo pessoal — não é um produto comercial.
