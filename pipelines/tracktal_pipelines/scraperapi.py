import asyncio
import logging

import httpx

logger = logging.getLogger(__name__)

SCRAPERAPI_BASE_URL = "https://api.scraperapi.com/"


class ScraperAPIError(Exception):
    pass


class ScraperAPIRateLimitError(ScraperAPIError):
    pass


class ScraperAPIServerError(ScraperAPIError):
    pass


class ScraperAPIClient:
    def __init__(self, api_key: str, max_concurrency: int = 5) -> None:
        self._api_key = api_key
        self._max_concurrency = max_concurrency
        self._client: httpx.AsyncClient | None = None
        self._semaphore: asyncio.Semaphore | None = None

    async def __aenter__(self) -> "ScraperAPIClient":
        self._client = httpx.AsyncClient(timeout=30.0)
        self._semaphore = asyncio.Semaphore(self._max_concurrency)
        return self

    async def __aexit__(self, *_: object) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
        self._semaphore = None
