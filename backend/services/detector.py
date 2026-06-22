"""
services/detector.py — Core fraud detection logic
  1. TF-IDF cosine similarity → duplicate / near-duplicate reviews
  2. Review-spike detection   → unusual bursts in rating/review volume
  3. Pattern rules            → fake signals (short reviews, emotional language, etc.)
  4. Sentiment mismatch       → optional HuggingFace pipeline
"""
import re
import numpy as np  # type: ignore
from collections import Counter, defaultdict
from datetime import datetime
from loguru import logger  # type: ignore

# sklearn — installed via requirements.txt
from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
from sklearn.metrics.pairwise import cosine_similarity  # type: ignore


# ── Constants ──────────────────────────────────────────────────────────────────

EMOTIONAL_MANIPULATION_PHRASES = [
    "best product ever", "life changing", "must buy", "do not hesitate",
    "absolutely love", "changed my life", "worth every penny", "exceeded expectations",
    "blown away", "never been happier", "perfect in every way", "buy this now",
    "amazing quality", "highly recommend", "you will not regret", "five stars",
    "exceeded all expectations", "outstanding product", "exactly as described",
]

SHORT_REVIEW_THRESHOLD = 15    # words — reviews below this are suspicious
HIGH_RATING_THRESHOLD  = 0.80  # if >80 % of ratings are 5★ → flag
SIMILARITY_THRESHOLD   = 0.75  # cosine similarity above this = near-duplicate
SPIKE_Z_SCORE          = 2.0   # std deviations above mean = spike


# ── Helpers ────────────────────────────────────────────────────────────────────

def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def _word_count(text: str) -> int:
    return len(text.split())


def _extract_stars(rating_str: str) -> int | None:
    """Parse '4.0 out of 5 stars' or '4★' → 4"""
    m = re.search(r"(\d+(?:\.\d+)?)", rating_str)
    return int(float(m.group(1))) if m else None


# ── 1. Similarity Analysis ─────────────────────────────────────────────────────

def compute_similarity_matrix(reviews: list[str]) -> np.ndarray:
    if len(reviews) < 2:
        return np.zeros((1, 1))
    cleaned = [_clean(r) for r in reviews]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, stop_words="english")
    try:
        tfidf  = vectorizer.fit_transform(cleaned)
        matrix = cosine_similarity(tfidf)
        return matrix
    except Exception as exc:
        logger.warning(f"TF-IDF failed: {exc}")
        return np.zeros((len(reviews), len(reviews)))


def find_duplicate_clusters(matrix: np.ndarray, threshold: float = SIMILARITY_THRESHOLD) -> list[set]:
    n = matrix.shape[0]
    visited  = set()
    clusters = []
    for i in range(n):
        if i in visited:
            continue
        cluster = {i}
        for j in range(i + 1, n):
            if matrix[i, j] >= threshold:
                cluster.add(j)
                visited.add(j)
        if len(cluster) > 1:
            clusters.append(cluster)
            visited.update(cluster)
    return clusters


# ── 2. Spike Detection ─────────────────────────────────────────────────────────

def detect_review_spikes(dates: list[str]) -> dict:
    """
    Groups reviews by month-year and flags months where volume
    exceeds mean + SPIKE_Z_SCORE * std.
    Returns dict with spike info.
    """
    parsed = []
    for d in dates:
        for fmt in ("%B %d, %Y", "%d %B %Y", "%Y-%m-%d", "%b %d, %Y", "%d/%m/%Y"):
            try:
                parsed.append(datetime.strptime(d[:20].strip(), fmt))
                break
            except ValueError:
                continue

    if not parsed:
        return {"spikes_detected": False, "spike_months": [], "monthly_counts": {}}

    counts: dict[str, int] = defaultdict(int)
    for dt in parsed:
        key = dt.strftime("%Y-%m")
        counts[key] += 1

    values = list(counts.values())
    mean   = np.mean(values)
    std    = np.std(values) if len(values) > 1 else 0
    threshold = mean + SPIKE_Z_SCORE * std

    spike_months = [month for month, cnt in counts.items() if cnt > threshold]

    return {
        "spikes_detected": bool(spike_months),
        "spike_months":    spike_months,
        "monthly_counts":  dict(sorted(counts.items())),
    }


# ── 3. Pattern Rules ───────────────────────────────────────────────────────────

def check_patterns(reviews: list[str], ratings: list[str]) -> dict:
    flags     = []
    scores    = []

    # Short reviews
    short = [r for r in reviews if _word_count(r) < SHORT_REVIEW_THRESHOLD]
    if len(short) > len(reviews) * 0.4:
        pct = round(len(short) / len(reviews) * 100)
        flags.append({
            "title":    "High volume of very short reviews",
            "detail":   f"{pct}% of reviews have fewer than {SHORT_REVIEW_THRESHOLD} words — often a sign of bot-generated content.",
            "severity": "medium",
        })
        scores.append(20)

    # Emotional manipulation
    em_count = sum(
        1 for r in reviews
        if any(phrase in r.lower() for phrase in EMOTIONAL_MANIPULATION_PHRASES)
    )
    if em_count > len(reviews) * 0.3:
        pct = round(em_count / len(reviews) * 100)
        flags.append({
            "title":    "Emotional manipulation language detected",
            "detail":   f"{pct}% of reviews contain high-pressure or generic praise phrases like 'life changing' or 'must buy immediately'.",
            "severity": "high",
        })
        scores.append(30)

    # 5-star concentration
    stars = [_extract_stars(r) for r in ratings if _extract_stars(r) is not None]
    if stars:
        five_star_ratio = stars.count(5) / len(stars)
        if five_star_ratio > HIGH_RATING_THRESHOLD:
            pct = round(five_star_ratio * 100)
            flags.append({
                "title":    f"Excessive 5-star concentration ({pct}%)",
                "detail":   f"{pct}% of ratings are 5-star — genuine products rarely receive near-perfect scores at this volume.",
                "severity": "high",
            })
            scores.append(25)

    # Copy-paste detection (exact duplicates)
    counts    = Counter([_clean(r) for r in reviews])
    exact_dup = sum(v - 1 for v in counts.values() if v > 1)
    if exact_dup > 0:
        flags.append({
            "title":    f"Copy-paste reviews detected ({exact_dup})",
            "detail":   f"{exact_dup} reviews are exact duplicates — a strong indicator of coordinated fake review campaigns.",
            "severity": "high",
        })
        scores.append(35)

    return {"flags": flags, "pattern_penalty": sum(scores)}


# ── 4. Rating Distribution ─────────────────────────────────────────────────────

def rating_distribution(ratings: list[str]) -> dict:
    dist: dict[str, int] = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
    for r in ratings:
        s = _extract_stars(r)
        if s and 1 <= s <= 5:
            dist[str(s)] += 1
    return dist


# ── 5. Sentiment Mismatch ──────────────────────────────────────────────────────

def analyze_sentiment_local(reviews: list[str]) -> dict:
    """
    Lightweight keyword-based fallback (no GPU needed).
    Returns positive / neutral / negative percentages.
    Falls back gracefully if transformers unavailable.
    """
    # Tier 1: HuggingFace transformers pipeline
    try:
        from transformers import pipeline as hf_pipeline  # type: ignore
        classifier = hf_pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            truncation=True,
            max_length=512,
        )
        sample = reviews[:50]
        results = classifier(sample)
        pos = sum(1 for r in results if r["label"] == "POSITIVE")
        neg = sum(1 for r in results if r["label"] == "NEGATIVE")
        total = max(len(results), 1)
        return {
            "positive": round(pos / total * 100, 1),
            "neutral":  round(0 / total * 100, 1),
            "negative": round(neg / total * 100, 1),
        }
    except Exception as exc:
        logger.debug(f"HuggingFace sentiment unavailable ({exc}), using keyword fallback")

    # Tier 2: Keyword bag-of-words fallback
    pos_words = {
        "great", "amazing", "love", "excellent", "perfect", "best",
        "fantastic", "wonderful", "recommend", "happy", "satisfied",
        "superb", "awesome", "outstanding", "flawless",
    }
    neg_words = {
        "terrible", "awful", "horrible", "worst", "hate", "disappointed",
        "poor", "defective", "broken", "useless", "refund",
        "scam", "fake", "waste", "regret", "avoid",
    }
    pos, neg, neu = 0, 0, 0
    for review in reviews:
        words = set(review.lower().split())
        p = len(words & pos_words)
        n = len(words & neg_words)
        if p > n:
            pos += 1
        elif n > p:
            neg += 1
        else:
            neu += 1
    total = max(len(reviews), 1)
    return {
        "positive": round(pos / total * 100, 1),
        "neutral":  round(neu / total * 100, 1),
        "negative": round(neg / total * 100, 1),
    }


# ── Main Analyzer ──────────────────────────────────────────────────────────────

def analyze_reviews(scraped: dict) -> dict:
    """
    Full detection pipeline. Returns structured data consumed by
    the OpenRouter AI layer and the response builder.
    """
    reviews = scraped.get("reviews", [])
    ratings = scraped.get("ratings", [])
    dates   = scraped.get("dates",   [])

    if not reviews:
        return {
            "error":             "No reviews found to analyze",
            "trust_penalty":     0,
            "flags":             [],
            "similarity_pct":    0,
            "clusters":          [],
            "spike_info":        {},
            "pattern_result":    {},
            "sentiment":         {},
            "rating_dist":       {},
        }

    # 1. Similarity
    sim_matrix = compute_similarity_matrix(reviews)
    clusters   = find_duplicate_clusters(sim_matrix)
    dup_count  = sum(len(c) for c in clusters)
    sim_pct    = round(dup_count / max(len(reviews), 1) * 100, 1)
    sim_penalty = min(sim_pct * 0.6, 40)   # max 40-point penalty

    # 2. Spikes
    spike_info = detect_review_spikes(dates)
    spike_penalty = 10 if spike_info["spikes_detected"] else 0

    # 3. Patterns
    pattern_result  = check_patterns(reviews, ratings)
    pattern_penalty = pattern_result["pattern_penalty"]

    # 4. Sentiment
    sentiment = analyze_sentiment_local(reviews)

    # 5. Rating dist
    rat_dist = rating_distribution(ratings)

    # Total penalty (trust score = 100 - penalties, floored at 0)
    total_penalty = sim_penalty + spike_penalty + pattern_penalty
    trust_score   = max(0, min(100, round(100 - total_penalty)))

    # Spike flag
    flags = list(pattern_result["flags"])
    if spike_info["spikes_detected"]:
        months_str = ", ".join(spike_info["spike_months"][:3])
        flags.append({
            "title":    "Abnormal review volume spike",
            "detail":   f"Unusual surge in reviews detected around {months_str} — this pattern is associated with purchased review campaigns.",
            "severity": "high",
        })

    # Similarity flag
    if sim_pct > 30:
        flags.append({
            "title":    f"High review similarity ({sim_pct}%)",
            "detail":   f"{dup_count} out of {len(reviews)} reviews share near-identical wording — suggesting templated or copy-paste reviews.",
            "severity": "high" if sim_pct > 60 else "medium",
        })

    return {
        "trust_score":    trust_score,
        "flags":          flags,
        "similarity_pct": sim_pct,
        "dup_count":      dup_count,
        "cluster_count":  len(clusters),
        "spike_info":     spike_info,
        "pattern_result": pattern_result,
        "sentiment":      sentiment,
        "rating_dist":    rat_dist,
        "total_reviews":  len(reviews),
    }
