"""Manual connectivity smoke test for ScraperAPI. Run: uv run python scripts/test_scraperapi.py"""
import asyncio

from tracktal_pipelines.scraperapi import ScraperAPIClient, ScraperAPIError


async def main() -> None:
    async with ScraperAPIClient.from_env() as client:
        try:
            html = await client.scrape("https://httpbin.org/get")
            print(f"OK — {len(html)} bytes returned")
        except ScraperAPIError as exc:
            print(f"FAIL — {exc}")


if __name__ == "__main__":
    asyncio.run(main())
