"""
services/scraper.py — Scrapes product reviews from Indian fashion & lifestyle platforms.
Supports: Myntra, Ajio, Nykaa Fashion, The Souled Store, Snitch, Bewakoof, Bonkers Corner, Tata CLiQ Fashion.
Falls back to realistic demo data when sites block the scraper.
"""
import asyncio
import random
import re
import httpx
from bs4 import BeautifulSoup
from loguru import logger
from config import get_settings

try:
    from playwright.async_api import async_playwright
except ImportError:
    async_playwright = None

settings = get_settings()

# Rotate user-agents to reduce bot detection
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
]

# Blocked-page signals (title substrings that indicate a bot-block / login wall)
BLOCKED_TITLES = [
    "sign in", "signin", "log in", "login", "robot check",
    "access denied", "captcha", "verify yourself", "not a robot",
]

# ── Supported platforms (allowlist) ───────────────────────────────────────────
# Only these domains are accepted by the /analyze endpoint.
SUPPORTED_DOMAINS = [
    "myntra.com",
    "ajio.com",
    "nykaa.com",
    "thesouledstore.com",
    "snitch.co.in",
    "bewakoof.com",
    "bonkerscorner.com",
    "tatacliq.com",
]

# ── CSS selectors per platform ────────────────────────────────────────────────
PLATFORM_SELECTORS = {
    "myntra": {
        "title":   [
            "h1.pdp-title", "h1.pdp-name", "h1[class*='title']",
            "div[class*='pdp-name']", "h1",
        ],
        "reviews": [
            "div.user-review-reviewTextWrapper p",
            "div[class*='reviewText'] p",
            "p[class*='reviewText']",
            "div.user-review-main",
            "p.user-review-reviewText",
            "[class*='reviewTextWrapper'] p",
            "[class*='review-text']",
        ],
        "ratings": [
            "div.user-review-rating span",
            "span[class*='user-review-rating']",
            "[class*='overallRatings'] span",
        ],
        "dates":   [
            "span.user-review-date",
            "[class*='review-date']",
            "span[class*='reviewDate']",
        ],
        "authors": [
            "span.user-review-author",
            "[class*='reviewer-name']",
            "span[class*='reviewAuthor']",
        ],
    },
    "ajio": {
        "title":   [
            "h1.prod-name", "h1[class*='prod-name']",
            "h1[class*='product-name']", "h1",
        ],
        "reviews": [
            "div[class*='review-description'] p",
            "p[class*='review-description']",
            "div[class*='review-text']",
            "p[class*='reviewText']",
            "div[class*='review-body']",
            "[itemprop='reviewBody']",
            "[class*='customer-review'] p",
        ],
        "ratings": [
            "div[class*='rating-value']",
            "span[class*='rating']",
            "[itemprop='ratingValue']",
        ],
        "dates": [
            "span[class*='review-date']",
            "p[class*='date']",
            "time",
        ],
        "authors": [
            "span[class*='reviewer-name']",
            "p[class*='customer-name']",
            "span[class*='author']",
        ],
    },
    "nykaa": {
        "title": [
            "h1[class*='product-title']", "h1[class*='title']",
            "span[class*='product-title']", "h1",
        ],
        "reviews": [
            "div[class*='review-description']",
            "p[class*='review-content']",
            "span[class*='review-content']",
            "div[class*='reviewContent']",
            "[itemprop='reviewBody']",
        ],
        "ratings": [
            "span[class*='star-rating']",
            "div[class*='rating-value']",
            "[itemprop='ratingValue']",
        ],
        "dates": [
            "span[class*='review-date']",
            "p[class*='review-date']",
            "time",
        ],
        "authors": [
            "span[class*='reviewer-name']",
            "p[class*='reviewer']",
            "[class*='author']",
        ],
    },
    "generic": {
        # Catches The Souled Store (Shopify), Snitch, Bewakoof, Bonkers Corner, Tata CLiQ etc.
        "title": ["h1"],
        "reviews": [
            "[data-hook='review-body'] span",
            "[class*='review-body']",
            "[class*='reviewBody']",
            "[class*='review-text']",
            "[class*='reviewText']",
            "[class*='review_body']",
            "[class*='comment-body']",
            "[itemprop='reviewBody']",
            "div[class*='review'] p",
            # Shopify Judge.me / Yotpo / Loox review widgets
            "[class*='jdgm'] [class*='body']",
            "[class*='yotpo'] [class*='content-review']",
            "span[class*='yotpo-review-content']",
            ".loox-rating span",
            "[class*='stamped'] [class*='review-content']",
        ],
        "ratings": [
            "[class*='rating']", "[class*='star']",
            "[itemprop='ratingValue']",
            "[class*='jdgm-rev__rating']",
        ],
        "dates": [
            "time", "[class*='date']", "[itemprop='datePublished']",
        ],
        "authors": [
            "[class*='author']", "[class*='user']",
            "[class*='reviewer']", "[itemprop='author']",
        ],
    },
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _detect_platform(url: str) -> str:
    url_lower = url.lower()
    if "myntra" in url_lower:
        return "myntra"
    if "ajio" in url_lower:
        return "ajio"
    if "nykaa" in url_lower:
        return "nykaa"
    # All other supported sites (Snitch, Souled Store, Bewakoof, Bonkers, Tata CLiQ)
    # use standard Shopify/WooCommerce review widgets → generic parser handles them
    return "generic"


def _extract_title_from_url(url: str) -> str:
    """Extracts a readable product title from a Myntra, Ajio, or other URL slug."""
    try:
        path = url.split("?")[0]
        parts = [p for p in path.split("/") if p]
        
        # Look for the slug part
        slug = ""
        if "myntra.com" in url:
            # e.g., .../hrx-by-hrithik-roshan-men-brand-logo-printed-shorts/39954510/buy
            # Look for the segment before the digit-only ID
            for i, part in enumerate(parts):
                if part.isdigit() and i > 0:
                    slug = parts[i - 1]
                    break
            if not slug and len(parts) >= 2:
                # Fallback to the second to last or last if no numeric ID found
                slug = parts[-2] if parts[-1] == "buy" else parts[-1]
        elif "ajio.com" in url:
            # e.g., .../gap-men-crew-neck-t-shirt/p/461234567_blue
            if "p" in parts:
                idx = parts.index("p")
                if idx > 0:
                    slug = parts[idx - 1]
        
        if not slug and parts:
            # General fallback: find the longest non-numeric part
            candidates = [p for p in parts if not p.isdigit() and p not in ("buy", "p", "dp", "gp") and "." not in p]
            if candidates:
                slug = max(candidates, key=len)
        
        if slug:
            # Replace hyphens, pluses, underscores with spaces and titlecase
            title = slug.replace("-", " ").replace("+", " ").replace("_", " ")
            return title.title()
    except Exception:
        pass
    return "Fashion Product"


def _is_blocked(title: str) -> bool:
    """Returns True if the page title suggests a bot-block or login wall."""
    t = title.lower()
    return any(sig in t for sig in BLOCKED_TITLES)


def _mock_reviews(url: str) -> dict:
    """
    Returns realistic demo review data for demonstration purposes.
    Used when the real scraper is blocked (e.g. anti-scraping walls).
    """
    logger.warning(f"[scraper] Site blocked scraper or returned 0 reviews. Using demo data for: {url}")

    demo_reviews = [
        "Absolutely love the fit and fabric! It's so comfortable for daily wear and looks premium.",
        "Absolutely love the fit and fabric! It's so comfortable for daily wear and looks premium.", # Duplicate 1
        "The material is nice, but the size runs a bit small. I recommend ordering one size up.",
        "Beautiful design and vibrant colors. The stitching is high quality. Completely satisfied!",
        "Beautiful design and vibrant colors. The stitching is high quality. Completely satisfied!", # Duplicate 2
        "Highly disappointed. The color faded after the very first wash, and the fit got loose.",
        "Great value for money. Looks exactly like the product photos. Will definitely buy again.",
        "Great value for money. Looks exactly like the product photos. Will definitely buy again.", # Duplicate 3
        "Fabric is average and feels a bit synthetic. Decent for rough use but not premium.",
        "Excellent product! The material is breathable and perfect for summer. Highly recommended.",
        "Stitching was coming off near the hem. Had to return it, but refund was quick.",
        "Stunning outfit. Got so many compliments when I wore it. True to size and matches description.",
        "It is okay. Color is slightly duller than shown in the picture, but fit is comfortable.",
        "Super soft fabric and perfect stitching. Always matches premium expectations!",
        "The styling is awesome, but the fabric is a magnet for lint. Needs frequent brushing.",
        "Very trendy and fits like a glove. Best clothing item I've bought online recently.",
        "Comfortable material, but it is somewhat transparent. Needs an inner layer.",
        "Worth every rupee. The quality of this brand is comparable to premium global labels.",
        "The fabric shrunk significantly after washing. Now it's too tight. Not recommended.",
        "Awesome casual wear. Light-weight and looks super cool. Delivery was super fast.",
        "The collar shape got distorted after one gentle wash. Poor durability.",
        "Amazing quality product! Exceeded my expectations. The shade of color is so aesthetic.",
        "Average quality. Stitching could be better, but for this discount price, it's fair.",
        "Absolute masterpiece! The details and fabric feel incredibly high-end. Must buy!",
        "Too long for my height, will need alteration. Otherwise, the design and quality are nice.",
        "Great texture and nice pattern. Feels very breathable and soft on skin.",
        "Received a defective piece with a small stain. Returning it today.",
        "Perfect dress! Fits beautifully and the color is gorgeous. Very satisfied with this purchase."
    ]

    demo_ratings = [
        "5", "5", "4", "5", "5", "1", "5", "5",
        "3", "5", "2", "5", "3",
        "5", "3", "5", "3", "5",
        "1", "4", "2", "5", "3",
        "5", "3", "4", "1", "5"
    ]

    demo_dates = [
        "15 Apr 2026", "15 Apr 2026", "03 Mar 2026", "20 Feb 2026", "20 Feb 2026", "08 Apr 2026", "01 Jan 2026", "01 Jan 2026",
        "12 Mar 2026", "25 Mar 2026", "18 Feb 2026", "30 Mar 2026", "05 Dec 2025",
        "02 Apr 2026", "10 Jan 2026", "07 Nov 2025", "14 Apr 2026", "22 Mar 2026",
        "15 Apr 2026", "03 Mar 2026", "20 Feb 2026", "08 Apr 2026", "01 Jan 2026",
        "12 Mar 2026", "25 Mar 2026", "18 Feb 2026", "30 Mar 2026", "05 Dec 2025"
    ]

    demo_authors = [
        "Rahul S.", "Rahul S.", "Priya M.", "Amit K.", "Amit K.", "Sneha R.", "Vikram T.", "Vikram T.",
        "Ananya B.", "Rohan G.", "Kavya P.", "Arjun N.", "Divya L.",
        "Suresh C.", "Meera J.", "Rajesh D.", "Pooja V.", "Kiran A.",
        "Rahul S.", "Priya M.", "Amit K.", "Sneha R.", "Vikram T.",
        "Ananya B.", "Rohan G.", "Kavya P.", "Arjun N.", "Divya L."
    ]

    title = _extract_title_from_url(url)
    if " (Demo Mode)" not in title:
        title += " (Demo Mode)"

    return {
        "title":   title,
        "url":     url,
        "reviews": demo_reviews,
        "ratings": demo_ratings,
        "dates":   demo_dates,
        "authors": demo_authors,
        "_demo":   True,   # flag so the router can add a warning header
    }


def _select_first(soup: BeautifulSoup, selector_list: list) -> list:
    """Try selectors in order; return results of the first that finds anything."""
    for sel in selector_list:
        try:
            results = [
                el.get_text(strip=True)
                for el in soup.select(sel)
                if el.get_text(strip=True)
            ]
            if results:
                logger.debug(f"[scraper] matched {sel!r} -> {len(results)} items")
                return results
        except Exception:
            continue
    return []


def _parse_html(html: str, selectors: dict, url: str, title_html: str = None) -> dict:
    soup = BeautifulSoup(html, "lxml")

    # Try title from dedicated product page first (Amazon redirect case)
    title = "Unknown Product"
    if title_html:
        tsoup = BeautifulSoup(title_html, "lxml")
        for sel in selectors["title"]:
            el = tsoup.select_one(sel)
            if el and el.get_text(strip=True):
                title = el.get_text(strip=True)
                break

    # Fallback: title from the scraped page itself
    if title == "Unknown Product":
        for sel in selectors["title"]:
            el = soup.select_one(sel)
            if el and el.get_text(strip=True):
                title = el.get_text(strip=True)
                break

    reviews = _select_first(soup, selectors["reviews"])
    ratings = _select_first(soup, selectors["ratings"])
    dates   = _select_first(soup, selectors["dates"])
    authors = _select_first(soup, selectors["authors"])

    # Filter noise (very short strings)
    reviews = [r for r in reviews if len(r) >= 4]

    logger.info(f"Scraped '{title[:60]}' -- {len(reviews)} reviews from {url}")

    return {
        "title":   title,
        "url":     url,
        "reviews": reviews[:200],
        "ratings": ratings[:200],
        "dates":   dates[:200],
        "authors": authors[:200],
    }


# ── Playwright scraper ────────────────────────────────────────────────────────

async def scrape_with_playwright(url: str) -> dict:
    """Primary scraper — renders JS, handles lazy-load, SPA pages."""
    if async_playwright is None:
        raise ImportError("Playwright is not installed")

    platform  = _detect_platform(url)
    selectors = PLATFORM_SELECTORS[platform]
    title_url = None

    async with async_playwright() as p:
        launch_args = {"headless": True}
        if settings.use_proxy and settings.proxy_url:
            launch_args["proxy"] = {"server": settings.proxy_url}

        browser = await p.chromium.launch(**launch_args)
        context = await browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1366, "height": 768},
            locale="en-US",
            timezone_id="America/New_York",
        )
        page = await context.new_page()

        # Anti-bot: mask webdriver fingerprint
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.navigator.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
        """)

        await page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2,ttf}", lambda r: r.abort())

        try:
            await page.goto(url, timeout=settings.scraper_timeout_seconds * 1000, wait_until="domcontentloaded")
        except Exception as e:
            logger.warning(f"[scraper] Playwright goto timed out or had issues: {e}. Proceeding with loaded content.")

        await page.wait_for_timeout(2000)

        for _ in range(3):
            await page.evaluate("window.scrollBy(0, document.body.scrollHeight / 3)")
            await page.wait_for_timeout(800)

        html = await page.content()

        title_html = None
        if title_url:
            try:
                await page.goto(title_url, timeout=15_000, wait_until="domcontentloaded")
                title_html = await page.content()
            except Exception:
                pass

        await browser.close()

    result = _parse_html(html, selectors, url, title_html=title_html)

    # Detect bot-block (sign-in wall)
    if _is_blocked(result["title"]) or len(result["reviews"]) == 0:
        logger.warning(f"[scraper] Blocked or 0 reviews from Playwright. Title: '{result['title']}'")
        raise RuntimeError("Site blocked the scraper (sign-in wall or 0 reviews)")

    return result


# ── httpx scraper ─────────────────────────────────────────────────────────────

async def scrape_with_httpx(url: str) -> dict:
    """Fallback scraper for static/server-rendered pages."""
    platform  = _detect_platform(url)
    selectors = PLATFORM_SELECTORS[platform]
    title_url = None

    proxy = settings.proxy_url if settings.use_proxy else None

    target_url = url
    target_title_url = title_url

    if settings.scraper_api_key and settings.scraper_api_key != "YOUR_FREE_SCRAPER_API_KEY_HERE":
        import urllib.parse
        target_url = f"http://api.scraperapi.com?api_key={settings.scraper_api_key}&url={urllib.parse.quote(url)}&render=true"
        if title_url:
            target_title_url = f"http://api.scraperapi.com?api_key={settings.scraper_api_key}&url={urllib.parse.quote(title_url)}&render=true"

    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }

    title_html = None
    async with httpx.AsyncClient(
        headers=headers,
        follow_redirects=True,
        timeout=25.0, # Fail faster so we fall back to Demo Mode instead of timing out the frontend
        proxy=proxy,
    ) as client:
        resp = await client.get(target_url)
        resp.raise_for_status()

        if target_title_url:
            try:
                t = await client.get(target_title_url)
                title_html = t.text
            except Exception:
                pass

    result = _parse_html(resp.text, selectors, url, title_html=title_html)

    if _is_blocked(result["title"]) or len(result["reviews"]) == 0:
        logger.warning(f"[scraper] Blocked or 0 reviews from httpx. Title: '{result['title']}'")
        raise RuntimeError("Site blocked the scraper (sign-in wall or 0 reviews)")

    return result


# ── Main entry point ──────────────────────────────────────────────────────────

async def scrape_product(url: str, retries: int = 1) -> dict:
    """
    Main entry point — tries Playwright first (except on Windows), falls back to httpx.
    If both fail (e.g. Amazon blocks the scraper), falls back to demo data
    so the full analysis pipeline can still run for demonstration purposes.
    """
    import sys
    last_err = None

    # Skip Playwright on Windows due to asyncio subprocess NotImplementedError
    skip_playwright = sys.platform == 'win32'
    if skip_playwright:
        logger.info("[scraper] Windows detected — skipping Playwright, using httpx directly")

    for attempt in range(retries):
        if not skip_playwright:
            try:
                return await scrape_with_playwright(url)
            except Exception as exc:
                last_err = exc
                logger.warning(f"Attempt {attempt + 1} Playwright failed: {exc}. Trying httpx...")

        try:
            return await scrape_with_httpx(url)
        except Exception as exc:
            last_err = exc
            if attempt < retries - 1:
                await asyncio.sleep(1.5)

    # Both scrapers failed — use demo data so the full pipeline still works
    logger.warning(f"[scraper] All attempts failed ({last_err}). Falling back to demo data.")
    return _mock_reviews(url)
