"""
AEGIS Forensic AI Text Detection Engine - Main Application Entrypoint.
Unifies REST API, HireCrew Seller-Hosted Adapter, and Model Context Protocol (MCP) server.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router
from app.hirecrew.routes import router as hirecrew_router
from app.mcp.server import mcp_server
from app.config import config

app = FastAPI(
    title=config.app_name,
    version=config.version,
    description=(
        "AEGIS is an enterprise-grade forensic analysis engine for detecting, attributing, "
        "and decomposing AI-generated, human-written, and hybrid/mixed content using a "
        "calibrated multi-layer architecture. Fully compatible with MCP and HireCrew marketplace."
    ),
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend and external integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Mount standard Forensic REST API router (/api/v1)
app.include_router(api_router)

# 2. Mount HireCrew Seller-Hosted API router (/jobs and /jobs/{jobId})
app.include_router(hirecrew_router)

# 3. Mount MCP Streamable HTTP / SSE transport (/mcp)
mcp_app = mcp_server.streamable_http_app()
app.mount("/mcp", mcp_app)


@app.get("/")
def root():
    return {
        "engine": config.app_name,
        "version": config.version,
        "status": "operational",
        "docs": "/docs",
        "health": "/api/v1/health",
        "hirecrew_seller_endpoint": "/jobs",
        "mcp_streamable_http_endpoint": "/mcp"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
