"""Image analysis API endpoints."""

import logging

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from starlette.concurrency import run_in_threadpool

from backend.models.schemas import ImageAnalysisResult, CivicAgentResult
from backend.services.gemma_service import GemmaService
from backend.agents.civic_agent import CivicAgent


logger = logging.getLogger(__name__)
router = APIRouter(tags=["analysis"])
gemma_service = GemmaService()
civic_agent = CivicAgent(gemma_service)


@router.post("/analyze", response_model=CivicAgentResult)
async def analyze_image(
    image: UploadFile = File(...),
    full_name: str = Form(...),
    contact_number: str = Form(...),
    location: str = Form(...),
) -> CivicAgentResult:
    """Analyze an uploaded civic issue image."""
    if not all(
        value.strip() for value in (full_name, contact_number, location)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Full name, contact number, and location are required.",
        )

    try:
        image_bytes = await image.read()
    except Exception as exc:
        logger.exception("Failed to read uploaded image")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to read the uploaded image.",
        ) from exc
    finally:
        try:
            await image.close()
        except Exception:
            logger.warning("Failed to close uploaded image", exc_info=True)

    try:
        return await run_in_threadpool(
            civic_agent.run,
            full_name,
            contact_number,
            location,
            image_bytes,
            
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception("Image analysis failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Image analysis failed.",
        ) from exc
