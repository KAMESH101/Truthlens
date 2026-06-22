"""
services/openrouter.py — Calls OpenRouter API to generate
the AI verdict, explanation, and structured JSON output.
"""
import json
import httpx  # type: ignore
from loguru import logger  # type: ignore
from config import get_settings  # type: ignore

settings = get_settings()


SYSTEM_PROMPT = """
You are an AI-powered fraud detection system for e-commerce platforms.
Your role is to analyze product review data and produce a clear, human-friendly fraud assessment.

Rules:
- Be explainable rather than only predictive
- Be confident but not absolute — avoid words like "certainly" or "definitely"
- Avoid fear-based conclusions or alarmist language
- Keep explanations simple and jargon-free
- Never claim certainty without evidence
- Output ONLY valid JSON — no markdown, no preamble, no code fences

Output this exact JSON structure:
{
  "verdict": "<one of: Highly trustworthy | Mixed signals detected | Likely manipulated reviews detected | High risk product>",
  "explanation": "<2-3 sentence plain-English summary of why the product got this score>",
  "pattern_notes": ["<observation 1>", "<observation 2>", "<observation 3>"],
  "sentiment_summary": "<one sentence describing the overall sentiment vs rating consistency>"
}
"""


def _build_user_prompt(scraped: dict, analysis: dict) -> str:
    reviews_sample = scraped.get("reviews", [])[:15]
    demo_note = (
        "\n⚠️  NOTE: This analysis is running on SYNTHETIC DEMO DATA "
        "(the real scraper was blocked by the site). You MUST state clearly "
        "in the 'explanation' field that results are based on demo data.\n"
    ) if scraped.get("_demo") else ""
    return f"""{demo_note}
Product Title: {scraped.get('title', 'Unknown')}
Product URL: {scraped.get('url', '')}
Total Reviews Analyzed: {analysis.get('total_reviews', 0)}

=== DETECTION RESULTS ===
Trust Score (computed): {analysis.get('trust_score', 50)}/100
Review Similarity: {analysis.get('similarity_pct', 0)}%
Duplicate Review Count: {analysis.get('dup_count', 0)}
Similarity Clusters Found: {analysis.get('cluster_count', 0)}
Spike Detected: {analysis.get('spike_info', {}).get('spikes_detected', False)}
Spike Months: {', '.join(analysis.get('spike_info', {}).get('spike_months', [])) or 'None'}

=== SENTIMENT ===
Positive: {analysis.get('sentiment', {}).get('positive', 0)}%
Neutral:  {analysis.get('sentiment', {}).get('neutral', 0)}%
Negative: {analysis.get('sentiment', {}).get('negative', 0)}%

=== RATING DISTRIBUTION ===
{json.dumps(analysis.get('rating_dist', {}), indent=2)}

=== FLAGS DETECTED ===
{json.dumps(analysis.get('flags', []), indent=2)}

=== SAMPLE REVIEWS (first 15) ===
{chr(10).join(f"{i+1}. {r}" for i, r in enumerate(reviews_sample))}

Based on the above data, produce the JSON verdict.
"""


async def get_ai_verdict(scraped: dict, analysis: dict) -> dict:
    """
    Calls OpenRouter with the analysis context.
    Returns parsed dict with verdict, explanation, etc.
    Falls back to a rule-based verdict if the API is unavailable.
    """
    if not settings.openrouter_api_key or settings.openrouter_api_key.startswith("sk-or-xxx"):
        logger.warning("OpenRouter API key not set — using rule-based fallback verdict")
        return _fallback_verdict(analysis)

    prompt = _build_user_prompt(scraped, analysis)

    payload = {
        "model": settings.openrouter_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens":  600,
    }

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type":  "application/json",
        "HTTP-Referer":  "https://truthlens.app",   # optional but recommended by OpenRouter
        "X-Title":       "TruthLens",
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                settings.openrouter_base_url,
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        raw_text = data["choices"][0]["message"]["content"].strip()

        # Strip any accidental markdown fences
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]

        result = json.loads(raw_text)
        logger.info(f"OpenRouter verdict: {result.get('verdict')}")
        return result

    except httpx.HTTPStatusError as exc:
        logger.error(f"OpenRouter HTTP error {exc.response.status_code}: {exc.response.text}")
        return _fallback_verdict(analysis)
    except (json.JSONDecodeError, KeyError) as exc:
        logger.error(f"OpenRouter response parse error: {exc}")
        return _fallback_verdict(analysis)
    except Exception as exc:
        logger.error(f"OpenRouter unexpected error: {exc}")
        return _fallback_verdict(analysis)


def _fallback_verdict(analysis: dict) -> dict:
    """Rule-based verdict used when OpenRouter is unavailable."""
    score = analysis.get("trust_score", 50)

    if score >= 71:
        verdict     = "Highly trustworthy"
        explanation = (
            "Reviews appear genuine and varied. Sentiment aligns with ratings, "
            "and no significant manipulation patterns were detected. "
            "This product shows strong indicators of authentic customer feedback."
        )
    elif score >= 36:
        verdict     = "Mixed signals detected"
        explanation = (
            "Some suspicious patterns were found alongside genuine-looking reviews. "
            "There may be a mix of real and boosted reviews. "
            "Exercise caution and look for verified purchase badges."
        )
    elif score >= 15:
        verdict     = "Likely manipulated reviews detected"
        explanation = (
            "Multiple manipulation signals were found — including repetitive wording, "
            "unusual rating spikes, and emotionally charged language. "
            "This review profile is consistent with a coordinated fake review campaign."
        )
    else:
        verdict     = "High risk product"
        explanation = (
            "Severe manipulation indicators detected across nearly all review signals. "
            "The reviews appear heavily fabricated. "
            "We strongly recommend seeking independent sources before purchasing."
        )

    return {
        "verdict":          verdict,
        "explanation":      explanation,
        "pattern_notes":    [f["title"] for f in analysis.get("flags", [])[:3]],
        "sentiment_summary": "Sentiment distribution may not reflect genuine buyer experience.",
    }
