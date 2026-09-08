from fastapi import HTTPException

from app.clients.omdb import OmdbClient, OmdbProviderError
from app.config import Settings
from app.schemas.movies import MovieDetail, MovieSearchResponse, MovieSummary


def _normalize(value: str | None) -> str | None:
    if value is None or value == "N/A":
        return None
    return value


class MovieService:
    def __init__(self, settings: Settings, client: OmdbClient | None = None) -> None:
        self._settings = settings
        self._client = client or OmdbClient(settings)

    def _ensure_api_key(self) -> None:
        if not self._settings.omdb_api_key.strip():
            raise HTTPException(
                status_code=503,
                detail="Serviço de filmes indisponível",
            )

    async def search(self, query: str) -> MovieSearchResponse:
        self._ensure_api_key()
        try:
            payload = await self._client.search_movies(query)
        except OmdbProviderError as exc:
            raise HTTPException(
                status_code=502,
                detail="Falha ao consultar o provedor de filmes",
            ) from exc

        if self._is_invalid_api_key(payload):
            raise HTTPException(
                status_code=503,
                detail="Serviço de filmes indisponível",
            )

        if payload.get("Response") == "False":
            return MovieSearchResponse(query=query, results=[])

        results = [
            MovieSummary(
                title=item["Title"],
                year=item["Year"],
                imdb_id=item["imdbID"],
                type=item["Type"],
                poster_url=_normalize(item.get("Poster")),
            )
            for item in payload.get("Search", [])
        ]
        return MovieSearchResponse(query=query, results=results)

    async def get_by_imdb_id(self, imdb_id: str) -> MovieDetail:
        self._ensure_api_key()
        try:
            payload = await self._client.get_movie_by_imdb_id(imdb_id)
        except OmdbProviderError as exc:
            raise HTTPException(
                status_code=502,
                detail="Falha ao consultar o provedor de filmes",
            ) from exc

        if self._is_invalid_api_key(payload):
            raise HTTPException(
                status_code=503,
                detail="Serviço de filmes indisponível",
            )

        if payload.get("Response") == "False":
            raise HTTPException(status_code=404, detail="Filme não encontrado")

        return MovieDetail(
            title=payload["Title"],
            year=payload["Year"],
            imdb_id=payload["imdbID"],
            type=payload["Type"],
            poster_url=_normalize(payload.get("Poster")),
            rated=_normalize(payload.get("Rated")),
            released=_normalize(payload.get("Released")),
            runtime=_normalize(payload.get("Runtime")),
            genre=_normalize(payload.get("Genre")),
            director=_normalize(payload.get("Director")),
            writers=_normalize(payload.get("Writer")),
            actors=_normalize(payload.get("Actors")),
            plot=_normalize(payload.get("Plot")),
            language=_normalize(payload.get("Language")),
            country=_normalize(payload.get("Country")),
            awards=_normalize(payload.get("Awards")),
            imdb_rating=_normalize(payload.get("imdbRating")),
            imdb_votes=_normalize(payload.get("imdbVotes")),
        )

    @staticmethod
    def _is_invalid_api_key(payload: dict) -> bool:
        error = str(payload.get("Error", "")).lower()
        return "invalid api key" in error or "no api key" in error
