"""Configuration manager tests."""

import json

from outline_cli.config import ConfigManager


def test_load_config_allows_base_url_without_api_key(tmp_path, monkeypatch):
    """Optional config loading should still return non-auth settings."""
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"base_url": "https://example.com/api", "timeout": 45}), encoding="utf-8")

    monkeypatch.delenv("OUTLINE_API_KEY", raising=False)
    monkeypatch.delenv("OUTLINE_BASE_URL", raising=False)

    config = ConfigManager.load_config(config_path=config_path, require_api_key=False)

    assert config["base_url"] == "https://example.com/api"
    assert config["timeout"] == 45


def test_load_config_requires_valid_api_key(tmp_path, monkeypatch):
    """Required config loading should enforce API key validation."""
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"api_key": "ol_api_test"}), encoding="utf-8")

    monkeypatch.delenv("OUTLINE_API_KEY", raising=False)
    monkeypatch.delenv("OUTLINE_BASE_URL", raising=False)

    config = ConfigManager.load_config(config_path=config_path)

    assert config["api_key"] == "ol_api_test"
