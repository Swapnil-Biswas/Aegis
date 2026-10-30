"""
AEGIS Forensic AI Text Detection Engine - Main Application Entrypoint.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router
from app.config import config

app = FastAPI(
    title=config.app_name,
    version=config.version,
    description=(
        "AEGIS is an enterprise-grade forensic analysis engine for detecting, attributing, "
        "and decomposing AI-generated, human-written, and hybrid/mixed content using a "
        "calibrated multi-layer architecture."
    ),
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount forensic API router
app.include_router(api_router)


@app.get("/")
def root():
    return {
        "engine": config.app_name,
        "version": config.version,
        "status": "operational",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)

