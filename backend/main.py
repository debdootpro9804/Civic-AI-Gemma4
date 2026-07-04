"""FastAPI application entry point."""

from fastapi import FastAPI

from backend.routes.health import router as health_router


app = FastAPI(
    title="CivicAI API",
    description="Backend API for the CivicAI civic issue reporting platform.",
    version="0.1.0",
)

app.include_router(health_router)
