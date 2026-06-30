"""
main.py — FastAPI application entry point

Run locally:
    uvicorn main:app --reload --port 8000

Production:
    uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
"""
import asyncio
import sys

# Windows asyncio fix for Playwright subprocess creation
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from config import get_settings
from routers.analyze import router as analyze_router

settings = get_settings()

# ── Logging ───────────────────────────────────────────────────────────────────
logger.remove()

# Wrap stdout in UTF-8 to prevent UnicodeEncodeError on Windows cp1252 consoles
import io
_utf8_stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)

logger.add(
    _utf8_stdout,
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}",
    level="DEBUG" if settings.app_env == "development" else "INFO",
)
logger.add(
    "logs/truthlens.log",
    rotation="10 MB",
    retention="7 days",
    compression="zip",
    level="INFO",
)

# ── Rate limiter ──────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.rate_limit_per_minute}/minute"])

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title        = "TruthLens API",
    description  = "AI-powered fake review detection for e-commerce products.",
    version      = "1.0.0",
    docs_url     = "/docs",
    redoc_url    = "/redoc",
    openapi_url  = "/openapi.json",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS ──────────────────────────────────────────────────────────────────────
origins = settings.origins_list
# Explicitly guarantee the production Vercel frontend is allowed
prod_origin = "https://truthlens-sage.vercel.app"
if prod_origin not in origins:
    origins.append(prod_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = origins,
    allow_credentials = True,
    allow_methods     = ["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers     = ["*"],
)

# ── Request logging middleware ────────────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug(f">> {request.method} {request.url.path}")
    response = await call_next(request)
    logger.debug(f"<< {response.status_code}")
    return response

# ── Global error handler ──────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "Internal server error", "detail": str(exc)},
    )

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(analyze_router)

# ── Root ──────────────────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def root():
    return {
        "service": "TruthLens",
        "version": "1.0.0",
        "docs":    "/docs",
        "status":  "running",
    }

@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}

