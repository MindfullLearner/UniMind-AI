
import json

from fastapi.testclient import TestClient

from backend.main import app
from backend.logging_config import LOG_FILE


client = TestClient(app)


def test_health_request_is_logged():
    with open(LOG_FILE, "a+", encoding="utf-8") as log_file:
        log_file.seek(0, 2)
        previous_size = log_file.tell()

        response = client.get("/health")

        log_file.seek(previous_size)
        new_logs = log_file.read()

    assert response.status_code == 200
    assert new_logs.strip()

    log_entries = [
        json.loads(line)
        for line in new_logs.strip().splitlines()
    ]

    log_entry = next(
        entry for entry in log_entries
        if entry["logger"] == "unimind.requests"
    )

    assert log_entry["method"] == "GET"
    assert log_entry["path"] == "/health"
    assert log_entry["status_code"] == 200
    assert "response_time_ms" in log_entry


def test_unauthorized_request_is_logged(monkeypatch):
    monkeypatch.setenv("UNIMIND_API_KEY", "test-secret-key")

    with open(LOG_FILE, "a+", encoding="utf-8") as log_file:
        log_file.seek(0, 2)
        previous_size = log_file.tell()

        response = client.post(
            "/ask",
            json={
                "query": "What is Generative AI?",
                "mode": "rag"
            },
            headers={
                "X-API-Key": "wrong-test-key"
            }
        )

        log_file.seek(previous_size)
        new_logs = log_file.read()

    assert response.status_code == 401
    assert new_logs.strip()

    log_entries = [
        json.loads(line)
        for line in new_logs.strip().splitlines()
    ]

    log_entry = next(
        entry for entry in log_entries
        if entry["logger"] == "unimind.requests"
    )

    assert log_entry["method"] == "POST"
    assert log_entry["path"] == "/ask"
    assert log_entry["status_code"] == 401

    assert "wrong-test-key" not in new_logs
    assert "test-secret-key" not in new_logs
