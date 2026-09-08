import httpx

from app.config import Settings


class OmdbProviderError(Exception):
    """Raised when the OMDb HTTP call fails (network/timeout)."""


class OmdbClient:
    def __init__(self, settings: Settings) -> None:
        self._base_url = settings.omdb_base_url
        self._api_key = settings.omdb_api_key
        self._timeout = settings.omdb_timeout_seconds

    async def search_movies(self, query: str) -> dict:
        return await self._get({"s": query})

    async def get_movie_by_imdb_id(self, imdb_id: str) -> dict:
        return await self._get({"i": imdb_id})

    async def _get(self, params: dict) -> dict:
        request_params = {**params, "apikey": self._api_key}
        try:
            async with httpx.AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout,
            ) as client:
                response = await client.get("/", params=request_params)
                response.raise_for_status()
                return response.json()
        except (httpx.TimeoutException, httpx.NetworkError, httpx.HTTPError) as exc:
            raise OmdbProviderError("Falha ao consultar o provedor de filmes") from exc
