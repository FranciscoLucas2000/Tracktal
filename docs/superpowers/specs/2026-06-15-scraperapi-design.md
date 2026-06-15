# ScraperAPI Integration Design

**Ticket:** TRA-15  
**Date:** 2026-06-15  
**Status:** Approved

---

## Overview

Shared async ScraperAPI client in `pipelines/tracktal_pipelines/scraperapi.py`. Used by Indeed and LinkedIn scrapers. Handles auth, concurrency limiting, retry logic, and error reporting.

---

## Architecture

Single file module. No sub-packages. Scrapers import:

```python
from tracktal_pipelines.scraperapi import ScraperAPIClient
```

### File structure

```
pipelines/
└── tracktal_pipelines/
    ├── __init__.py
    ├── scraperapi.py        ← ScraperAPIClient class
    └── flows/
        └── .gitkeep

pipelines/scripts/
    └── test_scraperapi.py   ← manual smoke test script

pipelines/tests/
    └── test_scraperapi.py   ← pytest unit tests
```

---

## Client Interface

```python
class ScraperAPIClient:
    def __init__(self, api_key: str, max_concurrency: int = 5): ...
    async def __aenter__(self) -> "ScraperAPIClient": ...
    async def __aexit__(self, *_): ...

    @classmethod
    def from_env(cls) -> "ScraperAPIClient":
        """Read SCRAPERAPI_KEY and SCRAPERAPI_MAX_CONCURRENCY from env."""

    async def scrape(
        self,
        url: str,
        render: bool = False,
        country_code: str | None = None,  # "pt", "es"
        **extra_params,
    ) -> str:
        """Return response HTML/text. Raise ScraperAPIError after retries exhausted."""

    async def scrape_batch(
        self,
        urls: list[str],
        **kwargs,
    ) -> list[str | None]:
        """Scrape all URLs concurrently (semaphore-limited). None = failed URL."""
```

### Exceptions

- `ScraperAPIError` — non-retryable or retries exhausted
- `ScraperAPIRateLimitError(ScraperAPIError)` — 429, logged separately

### Retry policy

`tenacity` — 3 attempts, exponential backoff 1s → 2s → 4s, retry on 429 and 5xx only.

### Concurrency

`asyncio.Semaphore(max_concurrency)` wraps each `scrape()` call inside `scrape_batch()`. Default 5 (ScraperAPI free plan limit).

---

## Configuration

Two env vars added to `.env.example` and Railway:

| Var | Default | Notes |
|---|---|---|
| `SCRAPERAPI_KEY` | — | Required. Fails fast at instantiation if missing. |
| `SCRAPERAPI_MAX_CONCURRENCY` | `5` | Increase on paid plan upgrade. |

---

## Usage in Prefect Flows

```python
async with ScraperAPIClient.from_env() as client:
    results = await client.scrape_batch(urls, render=True, country_code="pt")
```

`render=True` passed only when target site requires JS rendering (Indeed, LinkedIn). Costs ~5x credits vs basic proxy.

---

## Connectivity Test

Manual smoke test script — run after Railway deploy:

```bash
uv run python scripts/test_scraperapi.py
```

Scrapes `https://httpbin.org/get`, prints byte count on success or error details on failure. No Prefect dependency.

---

## Tests

`tests/test_scraperapi.py` — mocks `httpx.AsyncClient`, covers:

1. Successful scrape returns HTML string
2. 429 response triggers retry (assert called 3 times)
3. Retries exhausted → `scrape_batch` returns `None` for that URL
4. Missing `SCRAPERAPI_KEY` → raises immediately at `from_env()`

---

## Dependencies

`tenacity` added to `pyproject.toml` dependencies. No other new deps — `httpx` already present.
