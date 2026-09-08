from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import StringConstraints

from app.clients.omdb import OmdbClient
from app.config import Settings, get_settings
from app.schemas.movies import MovieDetail, MovieSearchResponse
from app.services.movies import MovieService

router = APIRouter(prefix="/movies", tags=["movies"])

ImdbId = Annotated[str, StringConstraints(pattern=r"^tt\d+$")]


def get_movie_service(settings: Settings = Depends(get_settings)) -> MovieService:
    return MovieService(settings=settings, client=OmdbClient(settings))


@router.get("/search", response_model=MovieSearchResponse)
async def search_movies(
    q: Annotated[str, Query(min_length=1)],
    service: MovieService = Depends(get_movie_service),
) -> MovieSearchResponse:
    return await service.search(q)


@router.get("/{imdb_id}", response_model=MovieDetail)
async def get_movie(
    imdb_id: ImdbId,
    service: MovieService = Depends(get_movie_service),
) -> MovieDetail:
    return await service.get_by_imdb_id(imdb_id)
