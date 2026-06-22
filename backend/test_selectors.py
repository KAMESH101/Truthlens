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
    
    # Print the userReviewsContainer HTML if found
    container = soup.find(class_="detailed-reviews-userReviewsContainer")
    if container:
        print("Found detailed-reviews-userReviewsContainer! Let's print its child structure:")
        # Find all divs or spans inside
        children = container.find_all(recursive=False)
        print(f"Direct children count: {len(children)}")
        for idx, child in enumerate(children[:3]):
            print(f"\n--- Child {idx + 1} tag: {child.name}, classes: {child.get('class', [])} ---")
            # print first 1000 characters of child HTML
            print(child.prettify()[:1000])
    else:
        print("detailed-reviews-userReviewsContainer not found. Let's find any div/span that has 'user' or 'review' or 'author' in its classes:")
        matches = []
        for el in soup.find_all(class_=True):
            for c in el["class"]:
                if "review" in c.lower() or "rating" in c.lower() or "author" in c.lower() or "date" in c.lower():
                    matches.append((el.name, c, el.get_text(strip=True)[:100]))
        for m in sorted(list(set(matches)))[:30]:
            print(m)

if __name__ == "__main__":
    asyncio.run(main())
