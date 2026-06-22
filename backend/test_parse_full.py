import asyncio
import httpx
import urllib.parse
from config import get_settings
from services.scraper import _parse_html, _is_blocked, PLATFORM_SELECTORS

settings = get_settings()

async def main():
    url = "https://www.myntra.com/shorts/hrx+by+hrithik+roshan/hrx-by-hrithik-roshan-men-brand-logo-printed-shorts/39954510/buy"
    target_url = f"http://api.scraperapi.com?api_key={settings.scraper_api_key}&url={urllib.parse.quote(url)}&render=true"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(target_url)
        html = resp.text
        
    selectors = PLATFORM_SELECTORS["myntra"]
    result = _parse_html(html, selectors, url)
    
    print("=" * 60)
    print("Parsed result:")
    print(f"Title: {result['title']!r}")
    print(f"Reviews count: {len(result['reviews'])}")
    print(f"Ratings count: {len(result['ratings'])}")
    print(f"Dates count: {len(result['dates'])}")
    print(f"Authors count: {len(result['authors'])}")
    
    blocked = _is_blocked(result["title"])
    zero_reviews = len(result["reviews"]) == 0
    print(f"Is blocked by title? {blocked}")
    print(f"Is 0 reviews? {zero_reviews}")
    print(f"Will trigger fallback? {blocked or zero_reviews}")
    
    if result["reviews"]:
        print("\nSample reviews:")
        for r in result["reviews"][:3]:
            print(f"  - {r}")
            
    if result["ratings"]:
        print("\nSample ratings:")
        for r in result["ratings"][:3]:
            print(f"  - {r}")

if __name__ == "__main__":
    asyncio.run(main())
