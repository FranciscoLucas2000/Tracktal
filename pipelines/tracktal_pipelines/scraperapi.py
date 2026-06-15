import asyncio
import logging

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

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

    async def scrape(
        self,
        url: str,
        render: bool = False,
        country_code: str | None = None,
        **extra_params: object,
    ) -> str:
        params: dict[str, str] = {"api_key": self._api_key, "url": url}
        if render:
            params["render"] = "true"
        if country_code:
            params["country_code"] = country_code
        params.update({k: str(v) for k, v in extra_params.items()})

        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=4),
            retry=retry_if_exception_type((ScraperAPIRateLimitError, ScraperAPIServerError)),
            reraise=True,
        ):
            with attempt:
                response = await self._client.get(SCRAPERAPI_BASE_URL, params=params)
                if response.status_code == 429:
                    logger.warning("ScraperAPI rate limit hit: %s", url)
                    raise ScraperAPIRateLimitError(f"Rate limited: {url}")
                if response.status_code >= 500:
                    raise ScraperAPIServerError(f"{response.status_code}: {url}")
                if response.status_code >= 400:
                    raise ScraperAPIError(f"{response.status_code}: {url}")
                return response.text

        raise ScraperAPIError(f"Retries exhausted: {url}")  # never reached; satisfies type checker

    async def scrape_batch(
        self,
        urls: list[str],
        **kwargs: object,
    ) -> list[str | None]:
        async def _scrape_one(url: str) -> str | None:
            async with self._semaphore:
                try:
                    return await self.scrape(url, **kwargs)
                except ScraperAPIError as exc:
                    logger.warning("Failed to scrape %s: %s", url, exc)
                    return None

        return list(await asyncio.gather(*(_scrape_one(url) for url in urls)))
