# Quickstart da Feature 001

Guia curto depois que a implementação do `plan.md` existir.

## 1. Key OMDb

Siga a seção do `README.md` na raiz: criar conta free, ativar e-mail, copiar a key.

## 2. Subir a API

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # preencher OMDB_API_KEY
uvicorn app.main:app --reload
```

## 3. Smoke test

```bash
curl http://localhost:8000/health
curl "http://localhost:8000/movies/search?q=inception"
curl http://localhost:8000/movies/tt1375666
```

## 4. Explorar

Abra http://localhost:8000/docs
