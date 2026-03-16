"""Client transport behavior tests."""

import errno
import json
import urllib.error

import pytest

import outline_cli.client as client_module
from outline_cli import OutlineAPIError, OutlineClient


class DummyResponse:
    """Minimal urllib response double for JSON payloads."""

    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def test_request_retries_transient_url_errors(monkeypatch):
    """Transient URLErrors should be retried before succeeding."""
    calls = {"count": 0}
    sleep_calls = []

    def fake_urlopen(request, timeout):
        calls["count"] += 1
        if calls["count"] < 3:
            raise urllib.error.URLError(OSError(errno.EBUSY, "Device or resource busy"))
        return DummyResponse({"ok": True})

    monkeypatch.setattr(client_module.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(client_module.time, "sleep", sleep_calls.append)

    client = OutlineClient(api_key="ol_api_test", base_url="https://example.com/api")
    result = client.documents_update(id="doc-1", text="hello")

    assert result == {"ok": True}
    assert calls["count"] == 3
    assert sleep_calls == [0.2, 0.5]


def test_request_reports_connection_context_after_retries(monkeypatch):
    """Exhausted transient URLErrors should include endpoint and payload context."""
    sleep_calls = []

    def fake_urlopen(request, timeout):
        raise urllib.error.URLError(OSError(errno.EBUSY, "Device or resource busy"))

    monkeypatch.setattr(client_module.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(client_module.time, "sleep", sleep_calls.append)

    client = OutlineClient(api_key="ol_api_test", base_url="https://example.com/api")

    with pytest.raises(OutlineAPIError) as exc_info:
        client.documents_update(id="doc-1", text="hello")

    message = str(exc_info.value)
    assert "documents.update" in message
    assert "https://example.com/api/documents.update" in message
    assert "payload_bytes=" in message
    assert "reason_type=OSError" in message
    assert "reason=[Errno 16] Device or resource busy" in message
    assert "reason_repr=OSError(16, 'Device or resource busy')" in message
    assert "attempts=3" in message
    assert sleep_calls == [0.2, 0.5]
