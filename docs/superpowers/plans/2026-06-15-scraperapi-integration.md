# ScraperAPI Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Shared async `ScraperAPIClient` in `pipelines/tracktal_pipelines/scraperapi.py` — retry logic, concurrency limiting, error handling, and a manual smoke test.

**Architecture:** `ScraperAPIClient` is an async context manager wrapping `httpx.AsyncClient` + `asyncio.Semaphore`. `tenacity.AsyncRetrying` handles 3-attempt exponential backoff (1s→2s→4s) on 429 and 5xx. `scrape_batch()` fans out concurrently within semaphore limit. Note: implementation adds `ScraperAPIServerError(ScraperAPIError)` for 5xx to differentiate retryable vs non-retryable — spec requires retry on 5xx, this is the cleanest way to express that.

**Tech Stack:** Python 3.11+, httpx (already in deps), tenacity (new), pytest-asyncio (new dev dep)

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `pipelines/pyproject.toml` | Modify | Add `tenacity`, `pytest-asyncio` deps + pytest config |
| `pipelines/.env.example` | Modify | Add `SCRAPERAPI_KEY`, `SCRAPERAPI_MAX_CONCURRENCY` |
| `pipelines/tracktal_pipelines/scraperapi.py` | Create | `ScraperAPIClient` class + exceptions |
| `pipelines/tests/test_scraperapi.py` | Create | pytest unit tests (all behaviour) |
| `pipelines/scripts/test_scraperapi.py` | Create | Manual smoke test (run after Railway deploy) |

---

### Task 1: Add dependencies and env var config

**Files:**
- Modify: `pipelines/pyproject.toml`
- Modify: `pipelines/.env.example`

- [ ] **Step 1: Add tenacity + pytest-asyncio to pyproject.toml**

Replace the `[project]` dependencies and `[dependency-groups]` sections:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "tracktal-pipelines"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "prefect>=3.0.0",
    "dbt-core>=1.8.0",
    "dbt-postgres>=1.8.0",
    "duckdb>=0.10.0",
    "anthropic>=0.26.0",
    "supabase>=2.4.0",
    "python-dotenv>=1.0.0",
    "httpx>=0.27.0",
    "tenacity>=8.0.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
]

[tool.hatch.build.targets.wheel]
packages = ["tracktal_pipelines"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
```

- [ ] **Step 2: Add env vars to .env.example**

Append to `pipelines/.env.example`:

```
# ScraperAPI
SCRAPERAPI_KEY=
SCRAPERAPI_MAX_CONCURRENCY=5
```

- [ ] **Step 3: Install updated deps**

```bash
cd pipelines && uv sync
```

Expected: resolves and installs tenacity + pytest-asyncio with no errors.

- [ ] **Step 4: Commit**

```bash
git add pipelines/pyproject.toml pipelines/.env.example
git commit -m "feat(TRA-15): add tenacity and pytest-asyncio deps, add ScraperAPI env vars"
```

---

### Task 2: Exceptions + ScraperAPIClient skeleton

**Files:**
- Create: `pipelines/tracktal_pipelines/scraperapi.py`
- Create: `pipelines/tests/test_scraperapi.py`

- [ ] **Step 1: Write failing tests for exceptions and client skeleton**

Create `pipelines/tests/test_scraperapi.py`:

```python
import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from tracktal_pipelines.scraperapi import (
    ScraperAPIClient,
    ScraperAPIError,
    ScraperAPIRateLimitError,
    ScraperAPIServerError,
)


# --- Helpers ---

def make_client(api_key: str = "test-key", max_concurrency: int = 5) -> ScraperAPIClient:
    """Return ScraperAPIClient with mocked httpx internals (skip context manager)."""
    client = ScraperAPIClient(api_key=api_key, max_concurrency=max_concurrency)
    client._client = AsyncMock()
    client._semaphore = asyncio.Semaphore(max_concurrency)
    return client


def mock_response(status_code: int, text: str = "<html/>") -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = text
    return resp


# --- Exception hierarchy ---

def test_scraperapi_error_is_exception():
    assert issubclass(ScraperAPIError, Exception)


def test_rate_limit_error_is_scraperapi_error():
    assert issubclass(ScraperAPIRateLimitError, ScraperAPIError)


def test_server_error_is_scraperapi_error():
    assert issubclass(ScraperAPIServerError, ScraperAPIError)


# --- Client skeleton ---

def test_client_stores_api_key():
    client = ScraperAPIClient(api_key="my-key")
    assert client._api_key == "my-key"


def test_client_stores_max_concurrency():
    client = ScraperAPIClient(api_key="key", max_concurrency=3)
    assert client._max_concurrency == 3


def test_client_default_max_concurrency():
    client = ScraperAPIClient(api_key="key")
    assert client._max_concurrency == 5


async def test_context_manager_creates_client_and_semaphore():
    async with ScraperAPIClient(api_key="key", max_concurrency=2) as client:
        assert client._client is not None
        assert isinstance(client._semaphore, asyncio.Semaphore)


async def test_context_manager_closes_client_on_exit():
    async with ScraperAPIClient(api_key="key") as client:
        inner_client = client._client

    # After exit, _client should be None
    assert client._client is None
```

- [ ] **Step 2: Run tests — expect failure**

```bash
cd pipelines && uv run pytest tests/test_scraperapi.py -v
```

Expected: `ImportError` — `scraperapi` module does not exist yet.

- [ ] **Step 3: Create scraperapi.py with skeleton**

Create `pipelines/tracktal_pipelines/scraperapi.py`:

```python
import asyncio
import logging

import httpx

logger = logging.getLogger(__name__)

SCRAPERAPI_BASE_URL = "http://api.scraperapi.com/"


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
```

- [ ] **Step 4: Run tests — expect pass**

```bash
cd pipelines && uv run pytest tests/test_scraperapi.py -v
```

Expected: all 9 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add pipelines/tracktal_pipelines/scraperapi.py pipelines/tests/test_scraperapi.py
git commit -m "feat(TRA-15): add ScraperAPIClient skeleton and exceptions"
```

---

### Task 3: `scrape()` with retry logic

**Files:**
- Modify: `pipelines/tracktal_pipelines/scraperapi.py`
- Modify: `pipelines/tests/test_scraperapi.py`

- [ ] **Step 1: Add failing tests for scrape()**

Append to `pipelines/tests/test_scraperapi.py`:

```python
from unittest.mock import patch


# --- scrape() ---

async def test_scrape_success_returns_text():
    client = make_client()
    client._client.get = AsyncMock(return_value=mock_response(200, "<html>OK</html>"))

    result = await client.scrape("https://example.com")

    assert result == "<html>OK</html>"


async def test_scrape_builds_correct_params():
    client = make_client(api_key="abc123")
    client._client.get = AsyncMock(return_value=mock_response(200, "ok"))

    await client.scrape("https://example.com", render=True, country_code="pt")

    call_kwargs = client._client.get.call_args
    params = call_kwargs.kwargs["params"]
    assert params["api_key"] == "abc123"
    assert params["url"] == "https://example.com"
    assert params["render"] == "true"
    assert params["country_code"] == "pt"


async def test_scrape_400_raises_scraperapi_error():
    client = make_client()
    client._client.get = AsyncMock(return_value=mock_response(403))

    with pytest.raises(ScraperAPIError):
        await client.scrape("https://example.com")


async def test_scrape_429_raises_rate_limit_error_after_retries():
    client = make_client()
    client._client.get = AsyncMock(return_value=mock_response(429))

    with patch("asyncio.sleep", new_callable=AsyncMock):
        with pytest.raises(ScraperAPIRateLimitError):
            await client.scrape("https://example.com")

    assert client._client.get.call_count == 3


async def test_scrape_500_raises_server_error_after_retries():
    client = make_client()
    client._client.get = AsyncMock(return_value=mock_response(500))

    with patch("asyncio.sleep", new_callable=AsyncMock):
        with pytest.raises(ScraperAPIServerError):
            await client.scrape("https://example.com")

    assert client._client.get.call_count == 3


async def test_scrape_retries_then_succeeds():
    client = make_client()
    client._client.get = AsyncMock(
        side_effect=[
            mock_response(429),
            mock_response(200, "<html>OK</html>"),
        ]
    )

    with patch("asyncio.sleep", new_callable=AsyncMock):
        result = await client.scrape("https://example.com")

    assert result == "<html>OK</html>"
    assert client._client.get.call_count == 2
```

- [ ] **Step 2: Run tests — expect failure**

```bash
cd pipelines && uv run pytest tests/test_scraperapi.py -v -k "scrape"
```

Expected: `AttributeError` — `scrape` not defined.

- [ ] **Step 3: Implement scrape()**

Add imports at top of `pipelines/tracktal_pipelines/scraperapi.py`:

```python
import os

from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
```

Add `scrape()` method to `ScraperAPIClient` (inside the class, after `__aexit__`):

```python
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
```

- [ ] **Step 4: Run tests — expect pass**

```bash
cd pipelines && uv run pytest tests/test_scraperapi.py -v
```

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add pipelines/tracktal_pipelines/scraperapi.py pipelines/tests/test_scraperapi.py
git commit -m "feat(TRA-15): implement scrape() with tenacity retry on 429/5xx"
```

---

### Task 4: `scrape_batch()` with semaphore concurrency

**Files:**
- Modify: `pipelines/tracktal_pipelines/scraperapi.py`
- Modify: `pipelines/tests/test_scraperapi.py`

- [ ] **Step 1: Add failing tests for scrape_batch()**

Append to `pipelines/tests/test_scraperapi.py`:

```python
# --- scrape_batch() ---

async def test_scrape_batch_returns_html_for_all_urls():
    client = make_client()
    client._client.get = AsyncMock(return_value=mock_response(200, "<html/>"))

    results = await client.scrape_batch(["https://a.com", "https://b.com"])

    assert results == ["<html/>", "<html/>"]


async def test_scrape_batch_returns_none_for_failed_url():
    client = make_client()
    client._client.get = AsyncMock(
        side_effect=[
            mock_response(200, "<html>A</html>"),
            mock_response(403),  # non-retryable error
        ]
    )

    results = await client.scrape_batch(["https://a.com", "https://b.com"])

    assert results[0] == "<html>A</html>"
    assert results[1] is None


async def test_scrape_batch_respects_concurrency_limit():
    """Semaphore limits concurrent calls — verify all URLs processed."""
    client = make_client(max_concurrency=2)
    client._client.get = AsyncMock(return_value=mock_response(200, "ok"))

    urls = [f"https://example.com/{i}" for i in range(10)]
    results = await client.scrape_batch(urls)

    assert len(results) == 10
    assert all(r == "ok" for r in results)
    assert client._client.get.call_count == 10


async def test_scrape_batch_preserves_url_order():
    """Results order matches input URLs order."""
    call_count = 0

    async def ordered_response(*args: object, **kwargs: object) -> MagicMock:
        nonlocal call_count
        call_count += 1
        return mock_response(200, f"result-{call_count}")

    client = make_client()
    client._client.get = ordered_response  # type: ignore[assignment]

    results = await client.scrape_batch(["https://a.com", "https://b.com", "https://c.com"])

    assert len(results) == 3
    # All are non-None strings
    assert all(isinstance(r, str) for r in results)
```

- [ ] **Step 2: Run tests — expect failure**

```bash
cd pipelines && uv run pytest tests/test_scraperapi.py -v -k "batch"
```

Expected: `AttributeError` — `scrape_batch` not defined.

- [ ] **Step 3: Implement scrape_batch()**

Add `scrape_batch()` method to `ScraperAPIClient` (after `scrape()`):

```python
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
```

- [ ] **Step 4: Run tests — expect pass**

```bash
cd pipelines && uv run pytest tests/test_scraperapi.py -v
```

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add pipelines/tracktal_pipelines/scraperapi.py pipelines/tests/test_scraperapi.py
git commit -m "feat(TRA-15): implement scrape_batch() with asyncio.Semaphore concurrency"
```

---

### Task 5: `from_env()` classmethod

**Files:**
- Modify: `pipelines/tracktal_pipelines/scraperapi.py`
- Modify: `pipelines/tests/test_scraperapi.py`

- [ ] **Step 1: Add failing tests for from_env()**

Append to `pipelines/tests/test_scraperapi.py`:

```python
import os


# --- from_env() ---

def test_from_env_reads_api_key(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("SCRAPERAPI_KEY", "my-secret-key")
    monkeypatch.delenv("SCRAPERAPI_MAX_CONCURRENCY", raising=False)

    client = ScraperAPIClient.from_env()

    assert client._api_key == "my-secret-key"


def test_from_env_default_concurrency(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("SCRAPERAPI_KEY", "key")
    monkeypatch.delenv("SCRAPERAPI_MAX_CONCURRENCY", raising=False)

    client = ScraperAPIClient.from_env()

    assert client._max_concurrency == 5


def test_from_env_custom_concurrency(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("SCRAPERAPI_KEY", "key")
    monkeypatch.setenv("SCRAPERAPI_MAX_CONCURRENCY", "10")

    client = ScraperAPIClient.from_env()

    assert client._max_concurrency == 10


def test_from_env_missing_key_raises(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("SCRAPERAPI_KEY", raising=False)

    with pytest.raises(KeyError):
        ScraperAPIClient.from_env()
```

- [ ] **Step 2: Run tests — expect failure**

```bash
cd pipelines && uv run pytest tests/test_scraperapi.py -v -k "from_env"
```

Expected: `AttributeError` — `from_env` not defined.

- [ ] **Step 3: Implement from_env()**

Add `from_env()` classmethod to `ScraperAPIClient` (after `__aexit__`, before `scrape()`):

```python
    @classmethod
    def from_env(cls) -> "ScraperAPIClient":
        api_key = os.environ["SCRAPERAPI_KEY"]
        max_concurrency = int(os.getenv("SCRAPERAPI_MAX_CONCURRENCY", "5"))
        return cls(api_key=api_key, max_concurrency=max_concurrency)
```

Also add `import os` to the top of the file if not already present.

- [ ] **Step 4: Run all tests — expect pass**

```bash
cd pipelines && uv run pytest tests/test_scraperapi.py -v
```

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add pipelines/tracktal_pipelines/scraperapi.py pipelines/tests/test_scraperapi.py
git commit -m "feat(TRA-15): add ScraperAPIClient.from_env() classmethod"
```

---

### Task 6: Manual smoke test script

**Files:**
- Create: `pipelines/scripts/test_scraperapi.py`

- [ ] **Step 1: Create scripts directory and smoke test**

```bash
mkdir -p pipelines/scripts
```

Create `pipelines/scripts/test_scraperapi.py`:

```python
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
```

- [ ] **Step 2: Verify script is importable (dry run without real key)**

```bash
cd pipelines && uv run python -c "import scripts.test_scraperapi" 2>&1 || true
```

Expected: either success (no output) or `KeyError: 'SCRAPERAPI_KEY'` — both mean the import path works. A `ModuleNotFoundError` for `tracktal_pipelines` means the install is broken.

- [ ] **Step 3: Run full test suite one final time**

```bash
cd pipelines && uv run pytest tests/ -v
```

Expected: all tests PASS, no warnings.

- [ ] **Step 4: Commit**

```bash
git add pipelines/scripts/test_scraperapi.py
git commit -m "feat(TRA-15): add manual ScraperAPI smoke test script"
```

---

## After Completion

Run smoke test against real Railway env to verify connectivity:

```bash
SCRAPERAPI_KEY=<your-key> uv run python scripts/test_scraperapi.py
```

Expected output: `OK — <N> bytes returned`
