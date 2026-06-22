import asyncio
import httpx
import urllib.parse
from bs4 import BeautifulSoup
from config import get_settings

settings = get_settings()

async def main():
    url = "https://www.myntra.com/shorts/hrx+by+hrithik+roshan/hrx-by-hrithik-roshan-men-brand-logo-printed-shorts/39954510/buy"
    target_url = f"http://api.scraperapi.com?api_key={settings.scraper_api_key}&url={urllib.parse.quote(url)}&render=true"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(target_url)
        html = resp.text
        
    soup = BeautifulSoup(html, "lxml")
    
    # Let's search for "review" in any class names
    print("Class names with 'review' in them:")
    classes = set()
    for el in soup.find_all(class_=True):
        for c in el["class"]:
            if "review" in c.lower() or "rating" in c.lower() or "pdp" in c.lower():
                classes.add(c)
    print(sorted(list(classes))[:30])

    print("\nText preview of elements matching reviews selectors:")
    selectors = [
        "div.user-review-reviewTextWrapper p",
        "div[class*='reviewText'] p",
        "p[class*='reviewText']",
        "div.user-review-main",
        "p.user-review-reviewText",
        "[class*='reviewTextWrapper'] p",
        "[class*='review-text']",
        "[class*='reviewText']"
    ]
    for sel in selectors:
        els = soup.select(sel)
        print(f"Selector {sel!r} found {len(els)} matches.")
        if els:
            print(f"  First match: {els[0].get_text(strip=True)[:100]}")

if __name__ == "__main__":
    asyncio.run(main())
