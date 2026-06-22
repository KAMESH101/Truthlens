"""
routers/analyze.py — POST /analyze  (main endpoint)
                      GET  /analyze/status/{job_id}  (async polling)
                      DELETE /analyze/cache  (cache invalidation)
"""
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from loguru import logger

from models.schemas import AnalyzeRequest, AnalyzeResponse, ErrorResponse
from services.scraper import scrape_product, SUPPORTED_DOMAINS
from services.detector import analyze_reviews
from services.openrouter import get_ai_verdict
from services.cache import get_cached, set_cached, invalidate
from utils.response_builder import build_response

router = APIRouter(prefix="/analyze", tags=["analyze"])


# ── Platform allowlist ────────────────────────────────────────────────────────

def _check_supported_platform(url: str) -> None:
    """Raise HTTPException 400 if the URL is not from a supported platform."""
    url_lower = url.lower()
    if not any(domain in url_lower for domain in SUPPORTED_DOMAINS):
        supported_names = "Myntra, Ajio, Nykaa Fashion, The Souled Store, Snitch, Bewakoof, Bonkers Corner, Tata CLiQ Fashion"
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "message": (
                    f"This platform is not supported. TruthLens only works with Indian "
                    f"fashion & lifestyle platforms: {supported_names}. "
                    f"Please paste a product link from one of these sites."
                ),
                "supported_platforms": supported_names,
            },
        )


@router.post(
    "",
    response_model=AnalyzeResponse,
    responses={
        400: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    summary="Analyze product reviews for fake signals",
    description="""
Accepts a product URL from supported Indian fashion platforms, scrapes reviews,
runs fraud detection, calls the OpenRouter AI model, and returns a structured trust report.

**Supported platforms:** Myntra, Ajio, Nykaa Fashion, The Souled Store, Snitch, Bewakoof, Bonkers Corner, Tata CLiQ Fashion

**Rate limited** to 10 requests per minute per IP.
Responses are **cached for 6 hours** per URL (Redis).
    """,
)
async def analyze(request: Request, body: AnalyzeRequest):
    url = body.url
    logger.info(f"[analyze] Request from {request.client.host} — {url}")

    # ── Platform validation ───────────────────────────────────────────────────
    _check_supported_platform(url)

    # ── Cache check ──────────────────────────────────────────────────────────

    cached_data = await get_cached(url)
    if cached_data:
        cached_data["cached"] = True
        # demo_mode is already stored in the cached dict from when it was first built
        return JSONResponse(content=cached_data)

    # ── Scrape ───────────────────────────────────────────────────────────────
    try:
        scraped = await scrape_product(url)
    except Exception as exc:
        logger.error(f"[analyze] Scraping failed: {exc}")
        raise HTTPException(
            status_code=422,
            detail={"success": False, "message": "Unable to scrape product page", "detail": str(exc)},
        )

    if not scraped.get("reviews"):
        raise HTTPException(
            status_code=422,
            detail={"success": False, "message": "No reviews found on this page. Try a direct product page URL."},
        )

    # ── Detection ────────────────────────────────────────────────────────────
    try:
        analysis = analyze_reviews(scraped)
    except Exception as exc:
        logger.error(f"[analyze] Detection failed: {exc}")
        raise HTTPException(
            status_code=500,
            detail={"success": False, "message": "Analysis pipeline error", "detail": str(exc)},
        )

    # ── OpenRouter AI ────────────────────────────────────────────────────────
    try:
        ai_verdict = await get_ai_verdict(scraped, analysis)
    except Exception as exc:
        logger.warning(f"[analyze] AI verdict failed, using fallback: {exc}")
        ai_verdict = {
            "verdict":          "Mixed signals detected",
            "explanation":      "AI analysis unavailable. Results are based on automated pattern detection only.",
            "pattern_notes":    [],
            "sentiment_summary": "",
        }

    # ── Build & cache response ───────────────────────────────────────────────
    demo_mode = scraped.get("_demo", False)
    response = build_response(scraped, analysis, ai_verdict, cached=False, demo_mode=demo_mode)
    response_dict = response.model_dump()

    await set_cached(url, response_dict)

    logger.info(f"[analyze] Done — score={response.trust_score}, verdict='{response.verdict}'")
    return response


@router.delete(
    "/cache",
    summary="Invalidate cached result for a URL",
)
async def clear_cache(url: str):
    await invalidate(url)
    return {"success": True, "message": f"Cache cleared for {url}"}


@router.get(
    "/health",
    summary="Health check for the analyze service",
)
async def health():
    return {"status": "ok", "service": "truthlens-analyze"}


@router.get(
    "/debug/scrape",
    summary="[DEBUG] Test scrape_product directly — shows raw scraper output",
    include_in_schema=False,
)
async def debug_scrape(url: str = "https://www.amazon.in/dp/B0D5Q5DX53"):
    from services.scraper import async_playwright as _ap
    scraped = await scrape_product(url)
    return {
        "playwright_available": _ap is not None,
        "title": scraped.get("title", ""),
        "reviews_count": len(scraped.get("reviews", [])),
        "ratings_count": len(scraped.get("ratings", [])),
        "demo_mode": scraped.get("_demo", False),
        "sample_reviews": scraped.get("reviews", [])[:3],
    }
