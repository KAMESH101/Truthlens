"""
utils/response_builder.py — Converts raw detection + AI verdict
into the final AnalyzeResponse Pydantic model.
"""
from models.schemas import (
    AnalyzeResponse, ReviewDNA, ChartsData, ChartDataPoint,
    RedFlag, RiskLevel,
)


def _risk_level(score: int) -> RiskLevel:
    if score >= 71:
        return RiskLevel.safe
    if score >= 36:
        return RiskLevel.caution
    return RiskLevel.risky


def _build_timeline(monthly_counts: dict) -> list[ChartDataPoint]:
    """monthly_counts: {"2024-01": 4, "2024-02": 12, ...}"""
    return [
        ChartDataPoint(label=month, value=count)
        for month, count in sorted(monthly_counts.items())
    ][-12:]   # last 12 months max


def _build_rating_dist(rating_dist: dict) -> list[ChartDataPoint]:
    return [
        ChartDataPoint(label=f"{k}★", value=v)
        for k, v in sorted(rating_dist.items())
    ]


def _build_sentiment_chart(sentiment: dict) -> list[ChartDataPoint]:
    return [
        ChartDataPoint(label="Positive", value=sentiment.get("positive", 0)),
        ChartDataPoint(label="Neutral",  value=sentiment.get("neutral",  0)),
        ChartDataPoint(label="Negative", value=sentiment.get("negative", 0)),
    ]


def build_response(
    scraped:     dict,
    analysis:    dict,
    ai_verdict:  dict,
    cached:      bool = False,
    demo_mode:   bool = False,
) -> AnalyzeResponse:

    trust_score = analysis.get("trust_score", 50)
    flags_raw   = analysis.get("flags", [])
    spike_info  = analysis.get("spike_info", {})
    sentiment   = analysis.get("sentiment",  {})
    rating_dist = analysis.get("rating_dist", {})

    flags = [
        RedFlag(
            title    = f["title"],
            detail   = f["detail"],
            severity = f.get("severity", "medium"),
        )
        for f in flags_raw
    ]

    monthly_counts = spike_info.get("monthly_counts", {})

    dna = ReviewDNA(
        similarity_percent = analysis.get("similarity_pct", 0),
        duplicate_count    = analysis.get("dup_count", 0),
        cluster_count      = analysis.get("cluster_count", 0),
        pattern_notes      = ai_verdict.get("pattern_notes", []),
    )

    charts = ChartsData(
        review_timeline    = _build_timeline(monthly_counts),
        rating_distribution = _build_rating_dist(rating_dist),
        sentiment_breakdown = _build_sentiment_chart(sentiment),
    )

    return AnalyzeResponse(
        success                = True,
        product_title          = scraped.get("title"),
        total_reviews_analyzed = analysis.get("total_reviews", 0),
        trust_score            = trust_score,
        risk_level             = _risk_level(trust_score),
        verdict                = ai_verdict.get("verdict", "Mixed signals detected"),
        flags                  = flags,
        dna                    = dna,
        charts                 = charts,
        sentiment_summary      = ai_verdict.get("sentiment_summary", ""),
        explanation            = ai_verdict.get("explanation", ""),
        cached                 = cached,
        demo_mode              = demo_mode,
    )
