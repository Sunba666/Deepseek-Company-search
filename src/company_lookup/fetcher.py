"""Data fetcher for quick company lookups."""

from typing import Any
from .plugins import manager


async def fetch_company_info(company_name: str) -> dict[str, Any]:
    """Fetch basic company information."""
    plugin = manager.get_plugin("company_info")
    if plugin:
        return await plugin.fetch(company_name)
    return {"error": "Plugin not found"}


async def fetch_all_data(company_name: str) -> dict[str, Any]:
    """Fetch all available data for a company."""
    return await manager.fetch_all(company_name)


async def fetch_quick(type_name: str, company_name: str) -> dict[str, Any]:
    """Fetch specific type of data quickly."""
    plugin = manager.get_plugin(type_name)
    if plugin:
        return await plugin.fetch(company_name)
    return {"error": f"Plugin '{type_name}' not found"}