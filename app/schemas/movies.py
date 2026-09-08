from pydantic import BaseModel, Field


class HealthStatus(BaseModel):
    status: str = Field(examples=["ok"])


class MovieSummary(BaseModel):
    title: str
    year: str
    imdb_id: str
    type: str
    poster_url: str | None = None


class MovieDetail(MovieSummary):
    rated: str | None = None
    released: str | None = None
    runtime: str | None = None
    genre: str | None = None
    director: str | None = None
    writers: str | None = None
    actors: str | None = None
    plot: str | None = None
    language: str | None = None
    country: str | None = None
    awards: str | None = None
    imdb_rating: str | None = None
    imdb_votes: str | None = None


class MovieSearchResponse(BaseModel):
    query: str
    results: list[MovieSummary]
