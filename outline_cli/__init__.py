"""
Outline CLI - A Python client and CLI for Outline knowledge bases.

This package provides both a Python API client and command-line interface
for interacting with Outline (https://www.getoutline.com/) knowledge bases.
"""

__version__ = "0.1.2"
__author__ = "VisualDust"
__email__ = "gavin@gong.host"

from .client import OutlineClient
from .config import ConfigManager
from .exceptions import (
    OutlineAPIError,
    OutlineAuthenticationError,
    OutlineConfigError,
    OutlineError,
    OutlineNotFoundError,
    OutlineValidationError,
)

__all__ = [
    "OutlineClient",
    "ConfigManager",
    "OutlineError",
    "OutlineAPIError",
    "OutlineConfigError",
    "OutlineAuthenticationError",
    "OutlineNotFoundError",
    "OutlineValidationError",
]
