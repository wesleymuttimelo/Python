def test_search_success(client):
    response = client.get("/movies/search", params={"q": "matrix"})
    assert response.status_code == 200
    body = response.json()
    assert body["query"] == "matrix"
    assert len(body["results"]) == 1
    assert body["results"][0]["imdb_id"] == "tt0133093"
    assert body["results"][0]["title"] == "The Matrix"


def test_search_empty_results(client_empty_search):
    response = client_empty_search.get("/movies/search", params={"q": "zzzzinexistente"})
    assert response.status_code == 200
    assert response.json() == {"query": "zzzzinexistente", "results": []}


def test_search_missing_q(client):
    response = client.get("/movies/search")
    assert response.status_code == 422


def test_search_empty_q(client):
    response = client.get("/movies/search", params={"q": ""})
    assert response.status_code == 422


def test_search_without_api_key(client_without_key):
    response = client_without_key.get("/movies/search", params={"q": "matrix"})
    assert response.status_code == 503
    assert response.json()["detail"] == "Serviço de filmes indisponível"


def test_search_invalid_api_key(client_invalid_key):
    response = client_invalid_key.get("/movies/search", params={"q": "matrix"})
    assert response.status_code == 503
    assert response.json()["detail"] == "Serviço de filmes indisponível"


def test_detail_success(client):
    response = client.get("/movies/tt0133093")
    assert response.status_code == 200
    body = response.json()
    assert body["imdb_id"] == "tt0133093"
    assert body["title"] == "The Matrix"
    assert body["plot"] is not None


def test_detail_not_found(client_not_found):
    response = client_not_found.get("/movies/tt0000000")
    assert response.status_code == 404
    assert response.json()["detail"] == "Filme não encontrado"


def test_detail_invalid_id(client):
    response = client.get("/movies/abc")
    assert response.status_code == 422


def test_detail_without_api_key(client_without_key):
    response = client_without_key.get("/movies/tt0133093")
    assert response.status_code == 503
    assert response.json()["detail"] == "Serviço de filmes indisponível"
