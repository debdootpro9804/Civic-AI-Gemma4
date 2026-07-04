"""Service health endpoints."""

from fastapi import APIRouter


router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Return the API readiness status."""
    return {"status": "ok"}
