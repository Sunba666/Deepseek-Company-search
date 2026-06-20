"""Base plugin class for all data fetchers."""

from abc import ABC, abstractmethod
from typing import Any


class BasePlugin(ABC):
    """Abstract base class for company data plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin identifier."""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable plugin name."""
        pass

    @abstractmethod
    def fetch(self, company_name: str, credit_code: str = None) -> dict:
        """Fetch data for the given company."""
        pass
