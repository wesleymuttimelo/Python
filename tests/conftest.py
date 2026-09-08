import pytest
from fastapi.testclient import TestClient

from app.clients.omdb import OmdbClient
from app.config import Settings, get_settings
from app.main import app
from app.services.movies import MovieService


SEARCH_PAYLOAD = {
    "Search": [
        {
            "Title": "The Matrix",
            "Year": "1999",
            "imdbID": "tt0133093",
            "Type": "movie",
            "Poster": "https://example.com/poster.jpg",
        }
    ],
    "totalResults": "1",
    "Response": "True",
}

EMPTY_SEARCH_PAYLOAD = {
    "Response": "False",
    "Error": "Movie not found!",
}

DETAIL_PAYLOAD = {
    "Title": "The Matrix",
    "Year": "1999",
    "imdbID": "tt0133093",
    "Type": "movie",
    "Poster": "https://example.com/poster.jpg",
    "Rated": "R",
    "Released": "31 Mar 1999",
    "Runtime": "136 min",
    "Genre": "Action, Sci-Fi",
    "Director": "Lana Wachowski, Lilly Wachowski",
    "Writer": "Lilly Wachowski, Lana Wachowski",
    "Actors": "Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss",
    "Plot": "A computer hacker learns about the true nature of reality.",
    "Language": "English",
    "Country": "United States, Australia",
    "Awards": "Won 4 Oscars.",
    "imdbRating": "8.7",
    "imdbVotes": "2,000,000",
    "Response": "True",
}

NOT_FOUND_PAYLOAD = {
    "Response": "False",
    "Error": "Movie not found!",
}

INVALID_KEY_PAYLOAD = {
    "Response": "False",
    "Error": "Invalid API key!",
}


class FakeOmdbClient(OmdbClient):
    def __init__(self, search_payload=None, detail_payload=None) -> None:
        self.search_payload = search_payload if search_payload is not None else SEARCH_PAYLOAD
        self.detail_payload = detail_payload if detail_payload is not None else DETAIL_PAYLOAD

    async def search_movies(self, query: str) -> dict:
        return self.search_payload

    async def get_movie_by_imdb_id(self, imdb_id: str) -> dict:
        return self.detail_payload


@pytest.fixture
def settings_with_key() -> Settings:
    return Settings(
        omdb_api_key="test-key",
        omdb_base_url="https://www.omdbapi.com/",
        omdb_timeout_seconds=10.0,
    )


@pytest.fixture
def settings_without_key() -> Settings:
    return Settings(
        omdb_api_key="",
        omdb_base_url="https://www.omdbapi.com/",
        omdb_timeout_seconds=10.0,
    )


@pytest.fixture
def client(settings_with_key: Settings):
    def _get_settings() -> Settings:
        return settings_with_key

    def _get_movie_service() -> MovieService:
        return MovieService(settings=settings_with_key, client=FakeOmdbClient())

    from app.api.routes.movies import get_movie_service

    app.dependency_overrides[get_settings] = _get_settings
    app.dependency_overrides[get_movie_service] = _get_movie_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def client_empty_search(settings_with_key: Settings):
    def _get_settings() -> Settings:
        return settings_with_key

    def _get_movie_service() -> MovieService:
        return MovieService(
            settings=settings_with_key,
            client=FakeOmdbClient(search_payload=EMPTY_SEARCH_PAYLOAD),
        )

    from app.api.routes.movies import get_movie_service

    app.dependency_overrides[get_settings] = _get_settings
    app.dependency_overrides[get_movie_service] = _get_movie_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def client_not_found(settings_with_key: Settings):
    def _get_settings() -> Settings:
        return settings_with_key

    def _get_movie_service() -> MovieService:
        return MovieService(
            settings=settings_with_key,
            client=FakeOmdbClient(detail_payload=NOT_FOUND_PAYLOAD),
        )

    from app.api.routes.movies import get_movie_service

    app.dependency_overrides[get_settings] = _get_settings
    app.dependency_overrides[get_movie_service] = _get_movie_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def client_without_key(settings_without_key: Settings):
    def _get_settings() -> Settings:
        return settings_without_key

    def _get_movie_service() -> MovieService:
        return MovieService(settings=settings_without_key, client=FakeOmdbClient())

    from app.api.routes.movies import get_movie_service

    app.dependency_overrides[get_settings] = _get_settings
    app.dependency_overrides[get_movie_service] = _get_movie_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def client_invalid_key(settings_with_key: Settings):
    def _get_settings() -> Settings:
        return settings_with_key

    def _get_movie_service() -> MovieService:
        return MovieService(
            settings=settings_with_key,
            client=FakeOmdbClient(
                search_payload=INVALID_KEY_PAYLOAD,
                detail_payload=INVALID_KEY_PAYLOAD,
            ),
        )

    from app.api.routes.movies import get_movie_service

    app.dependency_overrides[get_settings] = _get_settings
    app.dependency_overrides[get_movie_service] = _get_movie_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
