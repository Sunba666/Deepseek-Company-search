import json, logging
from typing import List, Dict
logger = logging.getLogger(__name__)

def consolidate_results(company_name: str, search_results: List[Dict]) -> Dict:
    if not search_results:
        return {"web_summary": "", "key_findings": [], "web_sources": 0}
    from .ai_analyzer import _call_deepseek_api
    lines = []
    for i, r in enumerate(search_results[:10], 1):
        t = r.get("title", "")
        u = r.get("url", "")
        c = r.get("content", "")[:300]
        lines.append(str(i) + ". [" + t + "](" + u + ")")
        lines.append("   " + c)
        lines.append("")
    txt = "\n".join(lines)
    sp = (
        "You are an intelligence analyst. Review web search results "
        + "for a company and produce a concise Chinese summary.\\n\\n"
        + 'Output ONLY valid JSON like {"web_summary":"...","key_findings":["..."],"pros":["..."],"cons":["..."]}\\n\\n'
        + "Only use info from results. Be honest if insufficient."
    )
    up = "Search results for " + company_name + ":\\n\\n" + txt
    response = _call_deepseek_api(up, sp)
    if response:
        try:
            clean = response.strip()
            if clean.startswith("```"):
                parts = clean.split("\\n", 1)
                if len(parts) > 1:
                    clean = parts[1]
                if clean.endswith("```"):
                    clean = clean[:-3]
            parsed = json.loads(clean.strip())
            parsed["web_sources"] = len(search_results)
            return parsed
        except Exception as e:
            logger.warning(f"[InfoAgg] parse failed: {e}")
    return {"web_summary": "", "key_findings": [], "pros": [], "cons": [],
            "web_sources": len(search_results)}
