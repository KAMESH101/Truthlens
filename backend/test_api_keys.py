import asyncio
import sys
import io
import httpx
from config import get_settings

# Force UTF-8 output on Windows cp1252 consoles
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)

settings = get_settings()

async def test_openrouter():
    print("Testing OpenRouter API Key...")
    print(f"  Model: {settings.openrouter_model}")
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": settings.openrouter_model,
        "messages": [{"role": "user", "content": "say hi"}],
        "max_tokens": 10
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(settings.openrouter_base_url, headers=headers, json=payload)
            if resp.status_code == 200:
                print("[PASS] OpenRouter API Key is VALID!")
                print(f"  Response: {resp.json()['choices'][0]['message']['content'].strip()}")
            elif resp.status_code == 401:
                print("[FAIL] OpenRouter API Key is EXPIRED or INVALID!")
                print(f"  Detail: {resp.text}")
            elif resp.status_code == 404:
                print(f"[FAIL] OpenRouter model '{settings.openrouter_model}' NOT FOUND (retired/invalid)!")
                print(f"  Detail: {resp.text}")
            else:
                print(f"[FAIL] OpenRouter returned status {resp.status_code}")
                print(f"  Detail: {resp.text}")
    except Exception as e:
        print(f"[FAIL] OpenRouter connection error: {e}")

async def test_scraper_api():
    print("\nTesting ScraperAPI Key...")
    if not settings.scraper_api_key or settings.scraper_api_key == "YOUR_FREE_SCRAPER_API_KEY_HERE":
        print("[SKIP] ScraperAPI Key is not configured.")
        return
    url = f"http://api.scraperapi.com?api_key={settings.scraper_api_key}&url=https://httpbin.org/ip"
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                print("[PASS] ScraperAPI Key is VALID!")
                print(f"  Proxy IP: {resp.text.strip()}")
            elif resp.status_code == 401 or resp.status_code == 403:
                print("[FAIL] ScraperAPI Key is EXPIRED or INVALID!")
                print(f"  Detail: {resp.text}")
            else:
                print(f"[FAIL] ScraperAPI returned status {resp.status_code}")
                print(f"  Detail: {resp.text}")
    except Exception as e:
        print(f"[FAIL] ScraperAPI connection error: {e}")

async def test_huggingface():
    print("\nTesting HuggingFace Token...")
    if not settings.hf_token:
        print("[SKIP] HuggingFace Token is not configured.")
        return
    headers = {"Authorization": f"Bearer {settings.hf_token}"}
    url = "https://huggingface.co/api/whoami-v2"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                print("[PASS] HuggingFace Token is VALID!")
                print(f"  User: {data.get('name', 'unknown')}")
            elif resp.status_code == 401:
                print("[FAIL] HuggingFace Token is EXPIRED or INVALID!")
                print(f"  Detail: {resp.text}")
            else:
                print(f"[FAIL] HuggingFace returned status {resp.status_code}")
                print(f"  Detail: {resp.text}")
    except Exception as e:
        print(f"[FAIL] HuggingFace connection error: {e}")

async def main():
    print("=" * 50)
    print("  TruthLens API Key Validation")
    print("=" * 50)
    await test_openrouter()
    await test_scraper_api()
    await test_huggingface()
    print("\n" + "=" * 50)
    print("  Done!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
