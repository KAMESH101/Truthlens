import asyncio
import os
from loguru import logger
import httpx

os.environ["SCRAPER_API_KEY"] = "a88485dd01bf331c8d0d47b0efa33324"

# Need to import config and scraper
import sys
sys.path.insert(0, r"c:\Users\kames\Desktop\Itzfizz Internship\truthlens\truthlens\backend")

from services.scraper import scrape_with_httpx

async def main():
    url = "https://www.amazon.in/dp/B0CHX1W1XY"
    try:
        res = await scrape_with_httpx(url)
        print("Success!")
        print(res["title"])
        print("Reviews:", len(res["reviews"]))
    except Exception as e:
        print("Failed:", str(e))

asyncio.run(main())
