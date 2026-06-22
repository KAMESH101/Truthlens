import asyncio
import httpx
import urllib.parse
import json

API_KEY = "a88485dd01bf331c8d0d47b0efa33324"

async def main():
    url = "https://www.amazon.in/product-reviews/B0CHX1W1XY?pageSize=50&sortBy=recent"
    target_url = f"http://api.scraperapi.com?api_key={API_KEY}&url={urllib.parse.quote(url)}&autoparse=true"
    
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.get(target_url)
        print("Status Code:", resp.status_code)
        try:
            data = resp.json()
            print("Title:", data.get("name", "Unknown"))
            reviews = data.get("reviews", [])
            print("Found Reviews:", len(reviews))
            if reviews:
                print("First review:", reviews[0].get("review", ""))
                print("Rating:", reviews[0].get("rating", ""))
                print("Date:", reviews[0].get("date", ""))
                print("Author:", reviews[0].get("author", ""))
        except Exception as e:
            print("Not JSON:", e)

asyncio.run(main())
