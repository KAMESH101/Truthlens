import asyncio
import os
import httpx
import urllib.parse

API_KEY = "a88485dd01bf331c8d0d47b0efa33324"

async def main():
    url = "https://www.flipkart.com/apple-iphone-15-black-128-gb/p/itm6ac6485515ae4"
    target_url = f"http://api.scraperapi.com?api_key={API_KEY}&url={urllib.parse.quote(url)}&render=true"
    
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.get(target_url)
        print("Status Code:", resp.status_code)
        
        # Test scraping using our TruthLens logic
        import sys
        sys.path.insert(0, r"c:\Users\kames\Desktop\Itzfizz Internship\truthlens\truthlens\backend")
        from services.scraper import _parse_html, PLATFORM_SELECTORS
        
        selectors = PLATFORM_SELECTORS["flipkart"]
        result = _parse_html(resp.text, selectors, url)
        
        print("Title:", result["title"])
        print("Found Reviews:", len(result["reviews"]))

asyncio.run(main())
