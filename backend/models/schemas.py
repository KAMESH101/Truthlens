"""
models/schemas.py — All Pydantic request & response schemas
"""
from pydantic import BaseModel, HttpUrl, field_validator
from typing import Optional
from enum import Enum


# ── Enums ─────────────────────────────────────────────────────────────────────

class RiskLevel(str, Enum):
    safe    = "safe"
    caution = "caution"
    risky   = "risky"


class VerdictLabel(str, Enum):
    highly_trustworthy         = "Highly trustworthy"
    mixed_signals              = "Mixed signals detected"
    likely_manipulated         = "Likely manipulated reviews detected"
    high_risk                  = "High risk product"


# ── Request ───────────────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        v = v.strip()
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v


# ── Sub-models ────────────────────────────────────────────────────────────────

class ReviewDNA(BaseModel):
    similarity_percent: float          # 0–100
    duplicate_count: int
    cluster_count: int
    pattern_notes: list[str]


class ChartDataPoint(BaseModel):
    label: str
    value: float


class ChartsData(BaseModel):
    review_timeline: list[ChartDataPoint]   # date → count
    rating_distribution: list[ChartDataPoint]  # 1★–5★ → count
    sentiment_breakdown: list[ChartDataPoint]  # positive / neutral / negative


class RedFlag(BaseModel):
    title: str
    detail: str
    severity: str   # "high" | "medium" | "low"


# ── Response ──────────────────────────────────────────────────────────────────

class AnalyzeResponse(BaseModel):
    success: bool
    product_title: Optional[str] = None
    total_reviews_analyzed: int = 0

    # Core verdict
    trust_score: int                   # 0–100
    risk_level: RiskLevel
    verdict: str

    # Detail
    flags: list[RedFlag]
    dna: ReviewDNA
    charts: ChartsData
    sentiment_summary: str
    explanation: str                   # plain-English AI explanation

    # Meta
    cached: bool = False
    demo_mode: bool = False   # True when scraper fell back to synthetic demo data


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    detail: Optional[str] = None
