import asyncio
import os
import httpx
import urllib.parse

API_KEY = "a88485dd01bf331c8d0d47b0efa33324"

async def main():
    url = "https://www.amazon.in/product-reviews/B0CHX1W1XY?pageSize=50&sortBy=recent"
    target_url = f"http://api.scraperapi.com?api_key={API_KEY}&url={urllib.parse.quote(url)}&render=true&premium=true"
    
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.get(target_url)
        with open("test_amazon.html", "w", encoding="utf-8") as f:
            f.write(resp.text)
        print("Saved to test_amazon.html")

asyncio.run(main())
