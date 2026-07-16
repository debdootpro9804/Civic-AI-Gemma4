"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.analyze import router as analyze_router
from backend.routes.health import router as health_router


app = FastAPI(
    title="CivicAI API",
    description="Backend API for the CivicAI civic issue reporting platform.",
    version="0.1.0",
)

app.include_router(analyze_router)
app.include_router(health_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)