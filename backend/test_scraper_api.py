import asyncio
import httpx
import urllib.parse
from config import get_settings

settings = get_settings()

async def main():
    url = "https://www.myntra.com/shorts/hrx+by+hrithik+roshan/hrx-by-hrithik-roshan-men-brand-logo-printed-shorts/39954510/buy"
    print("Testing ScraperAPI call via HTTPX directly...")
    print(f"API Key: {settings.scraper_api_key}")
    
    target_url = f"http://api.scraperapi.com?api_key={settings.scraper_api_key}&url={urllib.parse.quote(url)}&render=true"
    print(f"Querying: {target_url[:80]}...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(target_url, headers=headers)
            print(f"Status Code: {resp.status_code}")
            print(f"Response length: {len(resp.text)}")
            print("Preview:")
            print(resp.text[:1000])
    except Exception as e:
        print(f"Exception raised: {e}")

if __name__ == "__main__":
    asyncio.run(main())
