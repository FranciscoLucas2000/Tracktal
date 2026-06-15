import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tracktal_pipelines.scraperapi import (
    ScraperAPIClient,
    ScraperAPIError,
    ScraperAPIRateLimitError,
    ScraperAPIServerError,
)


# --- Helpers ---

def make_client(api_key: str = "test-key", max_concurrency: int = 5) -> ScraperAPIClient:
    """Return a ScraperAPIClient with _client replaced by AsyncMock and _semaphore pre-built.

    Bypasses __aenter__ so tests can call scrape()/scrape_batch() directly.
    Assign client._client.get return_value or side_effect to control HTTP responses.
    """
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
    mock_http_client = AsyncMock()

    async with ScraperAPIClient(api_key="key") as client:
        # Replace the real client with our mock to verify aclose() is called
        client._client = mock_http_client

    assert client._client is None
    mock_http_client.aclose.assert_awaited_once()


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

    assert client._client.get.call_count == 1


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


async def test_scrape_batch_processes_all_urls():
    """All URLs in the batch are processed; semaphore is exercised."""
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

    assert results == ["result-1", "result-2", "result-3"]


async def test_scrape_batch_empty_urls_returns_empty():
    client = make_client()
    results = await client.scrape_batch([])
    assert results == []


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

    with pytest.raises(ScraperAPIError, match="SCRAPERAPI_KEY"):
        ScraperAPIClient.from_env()


async def test_scrape_outside_context_manager_raises():
    client = ScraperAPIClient(api_key="key")
    with pytest.raises(RuntimeError, match="context manager"):
        await client.scrape("https://example.com")


async def test_scrape_batch_outside_context_manager_raises():
    client = ScraperAPIClient(api_key="key")
    with pytest.raises(RuntimeError, match="context manager"):
        await client.scrape_batch(["https://example.com"])
