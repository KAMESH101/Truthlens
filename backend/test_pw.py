import asyncio

from playwright.async_api import async_playwright

async def main():
    try:
        async with async_playwright() as p:
            print("Playwright async_playwright context opened successfully")
            browser = await p.chromium.launch(headless=True)
            print("Browser launched successfully!")
            await browser.close()
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(main())
