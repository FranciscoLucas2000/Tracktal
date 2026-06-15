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
