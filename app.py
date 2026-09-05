"""Master Application Entry Point for RiskLens AI.
Bootstraps database schema, verifies demo dataset, mounts API routes,
serves the pre-compiled frontend, and starts Uvicorn server on 0.0.0.0:8000.
Supports both local execution (python app.py) and cloud environments.
"""
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

# Ensure local directories are in python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

load_dotenv(os.path.join(BASE_DIR, ".env"))

from src.utils.logging_config import setup_logging
from src.database.database import init_db, check_db_connection
from src.database.seed_data import seed_database_if_empty
from src.api.customers import router as customers_router
from src.api.transactions import router as transactions_router
from src.api.investigations import router as investigations_router
from src.api.reports import router as reports_router

logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup lifecycle: initialize database schema and verify synthetic demo data."""
    logger.info("Starting RiskLens AI Application Service...")
    try:
        init_db()
        seed_database_if_empty()
    except Exception as e:
        logger.error("Database initialization warning during startup: %s", e)
    logger.info("Application bootstrap complete. Ready to serve requests.")
    yield


# Initialize FastAPI application
app = FastAPI(
    title="RiskLens AI",
    description="Evidence-First Banking Transaction Risk Investigation Assistant (NexusTiq24 PS06)",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
allowed_origins_env = os.environ.get("ALLOWED_ORIGINS", "")
if allowed_origins_env:
    allow_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
else:
    allow_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/api/health")
def health_check():
    """Production health check verifying database and AI availability."""
    db_health = check_db_connection()
    gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
    ai_status = "available" if gemini_key else "fallback_mode"

    is_healthy = db_health.get("status") == "connected"

    health_payload = {
        "status": "ok" if is_healthy else "degraded",
        "database": db_health.get("status", "unknown"),
        "ai": ai_status,
        "supabase": db_health.get("supabase", "not_configured"),
        "dialect": db_health.get("dialect", "unknown"),
        "service": "RiskLens AI",
        "version": "1.0.0",
        "success": is_healthy
    }
    health_payload["data"] = {
        "status": "healthy" if is_healthy else "degraded",
        "service": "RiskLens AI",
        "version": "1.0.0",
        "environment": "production",
        "port": 8000
    }
    return health_payload


# Mount API routers
app.include_router(customers_router)
app.include_router(transactions_router)
app.include_router(investigations_router)
app.include_router(reports_router)

# Mount compiled frontend if available
DIST_DIR = os.path.join(BASE_DIR, "frontend", "dist")
if os.path.exists(DIST_DIR):
    assets_dir = os.path.join(DIST_DIR, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Do not capture API routes
        if full_path.startswith("api/"):
            return JSONResponse(status_code=404, content={"success": False, "error": {"code": "NOT_FOUND", "message": "API route not found"}})
        target_file = os.path.join(DIST_DIR, full_path)
        if os.path.exists(target_file) and os.path.isfile(target_file):
            return FileResponse(target_file)
        # SPA Fallback to index.html
        index_file = os.path.join(DIST_DIR, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return JSONResponse(status_code=404, content={"message": "Frontend distribution not found."})
else:
    @app.get("/")
    def index_placeholder():
        return {
            "service": "RiskLens AI",
            "status": "Backend running. Frontend compilation in progress.",
            "health": "/api/health",
            "api_docs": "/docs"
        }


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False, log_level="info")
