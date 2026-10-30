"""
AEGIS Forensic AI Text Detection Engine - Main Application Entrypoint.
Unifies REST API, HireCrew Seller-Hosted Adapter, and Model Context Protocol (MCP) server.
"""

import contextlib
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.transport_security import TransportSecuritySettings
from app.api.endpoints import router as api_router
from app.hirecrew.routes import router as hirecrew_router
from app.mcp.server import mcp_server
from app.config import config

# MCP Streamable HTTP app serving POST /mcp. It is mounted at the root *after* all
# other routes (see bottom of file) so /mcp needs no redirect. Behind a public hostname, set
# AEGIS_ALLOWED_HOSTS (comma-separated) to keep DNS-rebinding protection on.
_allowed_hosts = [h.strip() for h in os.getenv("AEGIS_ALLOWED_HOSTS", "").split(",") if h.strip()]
mcp_app = mcp_server.streamable_http_app(
    streamable_http_path="/mcp",
    stateless_http=True,
    json_response=True,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=bool(_allowed_hosts),
        allowed_hosts=_allowed_hosts + ["127.0.0.1:*", "localhost:*"],
        allowed_origins=["*"],
    ),
)


@contextlib.asynccontextmanager
async def lifespan(_: FastAPI):
    # Mounted sub-apps do not get their own lifespan, so start the MCP session manager here.
    async with mcp_server.session_manager.run():
        yield


app = FastAPI(
    lifespan=lifespan,
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
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Mount standard Forensic REST API router (/api/v1)
app.include_router(api_router)

# 2. Mount HireCrew Seller-Hosted API router (/jobs and /jobs/{jobId})
app.include_router(hirecrew_router)



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


# 3. MCP Streamable HTTP transport (/mcp). Must stay the last route registered.
app.mount("/", mcp_app)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
