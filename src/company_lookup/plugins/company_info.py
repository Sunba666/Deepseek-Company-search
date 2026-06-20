"""Company info plugin with configurable API sources."""

import os
import requests
from .base import BasePlugin


class CompanyInfoPlugin(BasePlugin):
    @property
    def name(self):
        return "company_info"

    @property
    def display_name(self):
        return "工商信息"

    def fetch(self, company_name, credit_code=None):
        """Fetch company info from configured API or fallback to mock data."""
        # Try configured API first
        api_type = os.getenv("COMPANY_INFO_API", "")

        if api_type == "opencorporates":
            return self._fetch_from_opencorporates(company_name)
        elif api_type == "orsf":
            return self._fetch_from_orsf(company_name)
        else:
            # Fallback to mock data
            return self._get_mock_data(company_name)

    def _fetch_from_opencorporates(self, company_name):
        """Fetch from OpenCorporates API."""
        api_token = os.getenv("OPENCORPORATES_API_KEY", "")
        if not api_token:
            return {"error": "OpenCorporates API key not configured. Set OPENCORPORATES_API_KEY"}

        try:
            url = f"https://api.opencorporates.com/v0.4/companies/search"
            params = {"q": company_name, "api_token": api_token}
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if "results" in data and "companies" in data["results"]:
                companies = data["results"]["companies"]
                if companies:
                    company = companies[0]["company"]
                    return {
                        "name": company.get("name", ""),
                        "company_type": company.get("company_type", ""),
                        "jurisdiction_code": company.get("jurisdiction_code", ""),
                        "incorporation_date": company.get("incorporation_date", ""),
                        "current_status": company.get("current_status", ""),
                        "registered_address": company.get("registered_address", {}).get("locality", ""),
                        "source": "OpenCorporates"
                    }
            return {"error": "Company not found"}
        except Exception as e:
            return {"error": str(e)}

    def _fetch_from_orsf(self, company_name):
        """Fetch from ORSF API (Slovak companies only)."""
        try:
            url = "https://api.orsf.sk/v1/search"
            params = {"q": company_name}
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if "hits" in data and data["hits"]:
                company = data["hits"][0]
                return {
                    "name": company.get("name", ""),
                    "ico": company.get("ico", ""),
                    "legal_form": company.get("legalForm", ""),
                    "status": company.get("status", ""),
                    "city": company.get("city", ""),
                    "established_year": company.get("establishedYear", ""),
                    "is_vat_payer": company.get("isVatPayer", False),
                    "region": company.get("region", ""),
                    "source": "ORSF (Slovakia)"
                }
            return {"error": "Company not found"}
        except Exception as e:
            return {"error": str(e)}

    def _get_mock_data(self, company_name):
        """Return mock data when no API is configured."""
        return {
            "name": company_name,
            "credit_code": "91110108MA01XXXXX",
            "legal_person": "李四",
            "registered_capital": "500万元人民币",
            "status": "存续",
            "business_scope": "技术开发、咨询",
            "shareholders": ["李四(60%)", "王五(40%)"],
            "risk_items": [
                {"type": "被执行人", "date": "2025-06-01", "amount": "50万"}
            ],
            "note": "使用模拟数据。如需真实数据，请配置 COMPANY_INFO_API=opencorporates 或 orsf"
        }
