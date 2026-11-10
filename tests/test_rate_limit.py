
import pytest
from fastapi import HTTPException

from backend import main


TEST_API_KEY = "test-unimind-key"


@pytest.fixture(autouse=True)
def reset_rate_limit(monkeypatch):
    monkeypatch.setenv("UNIMIND_API_KEY", TEST_API_KEY)
    main.request_timestamps.clear()
    yield
    main.request_timestamps.clear()


def test_first_ten_requests_allowed(monkeypatch):
    monkeypatch.setattr(main.time, "monotonic", lambda: 1000.0)

    for _ in range(10):
        assert main.verify_api_key(TEST_API_KEY) is True


def test_eleventh_request_rejected(monkeypatch):
    monkeypatch.setattr(main.time, "monotonic", lambda: 1000.0)

    for _ in range(10):
        main.verify_api_key(TEST_API_KEY)

    with pytest.raises(HTTPException) as error:
        main.verify_api_key(TEST_API_KEY)

    assert error.value.status_code == 429
    assert error.value.headers["Retry-After"] == "60"


def test_requests_allowed_after_window(monkeypatch):
    current_time = [1000.0]

    monkeypatch.setattr(
        main.time,
        "monotonic",
        lambda: current_time[0]
    )

    for _ in range(10):
        main.verify_api_key(TEST_API_KEY)

    current_time[0] = 1061.0

    assert main.verify_api_key(TEST_API_KEY) is True


def test_invalid_api_key_rejected():
    with pytest.raises(HTTPException) as error:
        main.verify_api_key("wrong-key")

    assert error.value.status_code == 401
