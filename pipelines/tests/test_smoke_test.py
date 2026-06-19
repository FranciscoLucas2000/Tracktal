import pytest
from prefect.testing.utilities import prefect_test_harness
from tracktal_pipelines.flows.smoke_test import smoke_test


@pytest.fixture(autouse=True)
def prefect_setup():
    with prefect_test_harness():
        yield


def test_smoke_test_returns_ok():
    result = smoke_test()
    assert result == "ok"
