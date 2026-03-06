"""
Configuration management utilities for Outline CLI.

This module provides utilities for loading and managing configuration
for the Outline API client.
"""

import json
import os
from pathlib import Path
from typing import Any

from .exceptions import OutlineConfigError

ConfigDict = dict[str, Any]


class ConfigManager:
    """Manages configuration for Outline API client."""

    # Configuration file paths (in order of priority: project > user)
    DEFAULT_CONFIG_PATHS = [
        Path(".outline-skills") / "config.json",  # Project-level config
        Path.home() / ".outline-skills" / "config.json",  # User-level config
    ]

    DEFAULT_BASE_URL = "https://app.getoutline.com/api"
    DEFAULT_TIMEOUT = 30

    @classmethod
    def load_config(
        cls,
        config_path: Path | None = None,
        require_api_key: bool = True,
    ) -> ConfigDict:
        """
        Load configuration from file or environment.

        Args:
            config_path: Optional path to config file. If not provided,
                        will search default locations.
            require_api_key: Whether to require an API key to be present.

        Returns:
            Configuration dictionary with keys:
                - api_key: Outline API key
                - base_url: API base URL
                - timeout: Request timeout in seconds
                - default_collection: Optional default collection ID

        Raises:
            ValueError: If API key cannot be found
        """
        config: ConfigDict = {
            "base_url": cls.DEFAULT_BASE_URL,
            "timeout": cls.DEFAULT_TIMEOUT,
        }

        # Try to load from file
        if config_path:
            file_config = cls._load_from_file(config_path)
            if file_config:
                config.update(file_config)
        else:
            # Search default locations
            for path in cls.DEFAULT_CONFIG_PATHS:
                file_config = cls._load_from_file(path)
                if file_config:
                    config.update(file_config)
                    break

        # Override with environment variables
        env_api_key = os.getenv("OUTLINE_API_KEY")
        if env_api_key:
            config["api_key"] = env_api_key

        env_base_url = os.getenv("OUTLINE_BASE_URL")
        if env_base_url:
            config["base_url"] = env_base_url

        # Validate API key
        if require_api_key and "api_key" not in config:
            raise OutlineConfigError(
                "API key not found. Set OUTLINE_API_KEY environment variable "
                "or create a config file at .outline-skills/config.json or ~/.outline-skills/config.json"
            )

        api_key = config.get("api_key")
        if require_api_key and (not isinstance(api_key, str) or not api_key.startswith("ol_api_")):
            raise OutlineConfigError("Invalid API key format. API key should start with 'ol_api_'")

        return config

    @staticmethod
    def _load_from_file(path: Path) -> ConfigDict | None:
        """
        Load configuration from JSON file.

        Args:
            path: Path to config file

        Returns:
            Configuration dictionary or None if file doesn't exist or is invalid
        """
        if not path.exists():
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, dict):
                    return loaded
                print(f"Warning: Ignoring config from {path}: expected a JSON object")
                return None
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load config from {path}: {e}")
            return None

    @classmethod
    def create_config_file(
        cls,
        api_key: str,
        base_url: str | None = None,
        config_path: Path | None = None,
    ) -> Path:
        """
        Create a configuration file.

        Args:
            api_key: Outline API key
            base_url: Optional custom base URL
            config_path: Optional path for config file. Defaults to ~/.outline-skills/config.json

        Returns:
            Path to created config file

        Raises:
            IOError: If file creation fails
        """
        if config_path is None:
            config_path = cls.DEFAULT_CONFIG_PATHS[1]  # Use user-level config by default

        # Create directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)

        config = {
            "api_key": api_key,
            "base_url": base_url or cls.DEFAULT_BASE_URL,
            "timeout": cls.DEFAULT_TIMEOUT,
        }

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        # Set restrictive permissions on Unix systems
        if os.name != "nt":  # Not Windows
            os.chmod(config_path, 0o600)

        return config_path


def get_api_key() -> str:
    """
    Get API key from environment or config file.

    Returns:
        API key

    Raises:
        ValueError: If API key cannot be found
    """
    config = ConfigManager.load_config()
    api_key = config.get("api_key")
    if isinstance(api_key, str):
        return api_key
    raise OutlineConfigError("API key not found in configuration")


def get_base_url() -> str:
    """
    Get base URL from environment or config file.

    Returns:
        Base URL
    """
    config = ConfigManager.load_config(require_api_key=False)
    base_url = config.get("base_url")
    if isinstance(base_url, str):
        return base_url
    return ConfigManager.DEFAULT_BASE_URL
