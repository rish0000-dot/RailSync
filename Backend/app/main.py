"""RailSync 2.0 — FastAPI application entry point.

AI-Powered Automatic Block Planning & Digital Twin for Indian Railways.
Layer 4: API Orchestration + Persistence + Explanation + What-If + Feedback
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import feedback, health, negotiation, optimization, plans, risk, tasks
from app.core.config import settings
from app.core.logging import get_logger, setup_logging

# Path to built React frontend (populated by Docker multi-stage build)
_FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend_dist"

log = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    log.info("RailSync 2.0 Layer 4 starting up")

    # Eagerly verify DB connection at startup
    try:
        from app.db.database import check_db_health
        if check_db_health():
            log.info("Database connection verified")
        else:
            log.warning("Database connection failed — endpoints requiring DB will error")
    except Exception as e:
        log.warning("Database not configured: %s", e)

    yield
    log.info("RailSync 2.0 Layer 4 shutting down")


app = FastAPI(
    title="RailSync 2.0 — Layer 4 API",
    description=(
        "AI-Powered Automatic Block Planning & Digital Twin for Indian Railways.\n\n"
        "Orchestrates Layer 1 (Risk/ML), Layer 2 (Negotiation), and Layer 3 (CP-SAT Optimization) "
        "into a unified REST API for the React Dashboard.\n\n"
        "**Prototype Note:** This system uses synthetic/normalized data for demonstration. "
        "It does not have live production TMS/SMMS/TDMS/COA access."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

# CORS — allow configured origins + wildcard for HF Space deployment
_cors_origins = settings.cors_origin_list
if "*" not in _cors_origins:
    _cors_origins = ["*", *_cors_origins]  # HF Space needs wildcard

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(health.router)
app.include_router(tasks.router)
app.include_router(risk.router)
app.include_router(negotiation.router)
app.include_router(optimization.router)
app.include_router(plans.router)
app.include_router(feedback.router)

# ── Static frontend serving (production / HF Spaces) ──────────────────────
# Mount only when the frontend dist/ has been built (Docker stage 1 output).
if _FRONTEND_DIST.is_dir():
    # Serve static assets (JS, CSS, images)
    app.mount(
        "/assets",
        StaticFiles(directory=str(_FRONTEND_DIST / "assets")),
        name="frontend-assets",
    )

    @app.get("/", include_in_schema=False)
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str = ""):
        """Serve React SPA — return index.html for all non-API paths."""
        # Don't intercept API routes — they're already handled above
        api_prefixes = (
            "health", "risk", "tasks", "ingest", "negotiate",
            "optimize", "plan", "feedback", "docs", "openapi",
        )
        if any(full_path.startswith(p) for p in api_prefixes):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not found")

        # Serve exact file if it exists (favicon, manifest, etc.)
        file_path = _FRONTEND_DIST / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))

        # Fallback: React Router handles everything else
        return FileResponse(str(_FRONTEND_DIST / "index.html"))
