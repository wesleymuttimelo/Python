from fastapi import APIRouter

from app.schemas.movies import HealthStatus

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthStatus)
async def get_health() -> HealthStatus:
    return HealthStatus(status="ok")
