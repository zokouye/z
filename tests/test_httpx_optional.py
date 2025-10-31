import builtins

import pytest

from market_monitor import alerts
from market_monitor.collectors import base


def test_http_collector_missing_httpx(monkeypatch):
    original_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "httpx":
            raise ModuleNotFoundError("No module named 'httpx'")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(RuntimeError) as exc:
        base._require_httpx()

    assert "httpx is required" in str(exc.value)


def test_webhook_channel_requires_httpx(monkeypatch):
    original_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "httpx":
            raise ModuleNotFoundError("No module named 'httpx'")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(RuntimeError) as exc:
        alerts._post_json("https://example.com/webhook", {"content": "hi"})

    assert "httpx is required" in str(exc.value)
