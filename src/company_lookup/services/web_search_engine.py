import os, logging
from typing import List, Dict
logger = logging.getLogger(__name__)

def search_web(company_name: str, max_results: int = 10) -> List[Dict]:
    api_key = os.environ.get("TAVILY_API_KEY", "")
    if not api_key:
        logger.info("[WebSearch] Tavily not configured")
        return []
    import requests as _req
    queries = [
        company_name + " \u516c\u53f8 \u62db\u8058",
        company_name + " \u85aa\u8d44 \u5f85\u9047",
        company_name + " \u5458\u5de5 \u8bc4\u4ef7",
        company_name + " \u516c\u53f8 \u4ecb\u7ecd",
    ]
    seen_urls = set()
    all_results = []
    for query in queries:
        try:
            resp = _req.post(
                "https://api.tavily.com/search",
                json={"api_key": api_key, "query": query,
                      "max_results": 5, "search_depth": "basic",
                      "include_answer": False, "include_raw_content": False},
                timeout=10,
            )
            if resp.status_code == 200:
                for r in resp.json().get("results", []):
                    url = r.get("url", "")
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        all_results.append({
                            "title": r.get("title", ""),
                            "url": url,
                            "content": r.get("content", "")[:500],
                            "score": r.get("score", 0),
                        })
        except Exception as e:
            logger.warning(f"[WebSearch] Error: {e}")
    all_results.sort(key=lambda x: x.get("score", 0), reverse=True)
    return all_results[:max_results]
