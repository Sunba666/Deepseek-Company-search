"""DataMerger: 多源数据智能合并引擎。"""
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class DataMerger:
    """多源数据智能合并器。
    
    用法:
        merger = DataMerger(existing_data)
        merger.merge(new_data, source="tianyancha")
        merger.merge(another, source="tavily_search")
        merged = merger.data
    """

    # 来源优先级（数值越高越优先）
    SOURCE_PRIORITY = {
        "tianyancha": 100,
        "qichacha": 95,
        "user_feedback": 90,
        "deepseek_kb": 80,
        "court": 70,
        "tavily_search": 60,
        "mock": 10,
    }

    def __init__(self, existing_data: Optional[Dict] = None):
        self.data: Dict = existing_data or {}

    def merge(self, new_data: Dict, source: str) -> Dict:
        """合并新数据到现有数据。"""
        if not self.data:
            self.data = self._init_with_source(new_data, source)
            self.data["merged_at"] = datetime.now().isoformat()
            return self.data

        if "fields" not in self.data:
            self.data["fields"] = {}

        for field, new_value in new_data.items():
            if field.startswith("_"):
                continue  # 跳过元字段（_source, _raw）
            if field in ("canonical_name",):
                self._merge_name(new_value, source)
                continue
            if field == "aliases":
                self._merge_aliases(new_value)
                continue

            existing = self.data["fields"].get(field, {})
            merged = self._merge_field(field, new_value, existing, source)
            if merged:
                self.data["fields"][field] = merged

        self.data["merged_at"] = datetime.now().isoformat()
        return self.data

    def to_flat_dict(self) -> Dict:
        """展开为扁平 dict 供模板使用。
        
        返回格式:
            {"company_profile": "xxx", "legal_person": "xxx", ...}
        """
        flat = {}
        flat["canonical_name"] = self.data.get("canonical_name", "")
        flat["aliases"] = self.data.get("aliases", [])
        flat["merged_at"] = self.data.get("merged_at", "")

        for field_name, field_info in self.data.get("fields", {}).items():
            flat[field_name] = field_info.get("value", "")
            flat[f"{field_name}_sources"] = field_info.get("sources", [])
            flat[f"{field_name}_confidence"] = field_info.get("confidence", "low")

        return flat

    def _init_with_source(self, new_data: Dict, source: str) -> Dict:
        """首次接入，直接存储并标注来源。"""
        result = {}
        for field, value in new_data.items():
            if field.startswith("_"):
                continue
            if field == "canonical_name":
                result["canonical_name"] = value
                continue
            if field == "aliases":
                result["aliases"] = value
                continue
            if "fields" not in result:
                result["fields"] = {}
            result["fields"][field] = {
                "value": value,
                "sources": [source],
                "confidence": self._calc_confidence(source, value),
                "last_updated": datetime.now().isoformat(),
            }
        return result

    def _merge_field(self, field_name: str, new_value: Any,
                     existing: Dict, source: str) -> Dict:
        """合并单个字段。"""
        if not existing:
            return {
                "value": new_value,
                "sources": [source],
                "confidence": self._calc_confidence(source, new_value),
                "last_updated": datetime.now().isoformat(),
            }

        old_val = str(existing.get("value", ""))
        new_val = str(new_value)
        old_len = len(old_val)
        new_len = len(new_val)

        # 值相同：只补充来源
        if old_val == new_val:
            if source not in existing.get("sources", []):
                existing.setdefault("sources", []).append(source)
            return existing

        # 新来源更权威 或 新内容明显更丰富（1.5x+）
        if self._is_more_authoritative(source, existing.get("sources", [])) or \
           new_len > max(old_len * 1.5, 20):
            return {
                "value": new_value,
                "sources": existing.get("sources", []) + [source],
                "confidence": self._calc_confidence(source, new_value),
                "last_updated": datetime.now().isoformat(),
                "previous_value": existing.get("value"),
            }

        # 旧值更好：只追加来源
        if source not in existing.get("sources", []):
            existing.setdefault("sources", []).append(source)
        return existing

    def _is_more_authoritative(self, source: str, existing_sources: List[str]) -> bool:
        new_pri = self.SOURCE_PRIORITY.get(source, 50)
        existing_max = max((self.SOURCE_PRIORITY.get(s, 50) for s in existing_sources), default=0)
        return new_pri > existing_max

    def _calc_confidence(self, source: str, value: Any) -> str:
        if source in ("tianyancha", "qichacha"):
            return "high"
        if source == "user_feedback":
            return "high" if len(str(value)) > 20 else "medium"
        if len(str(value)) > 100:
            return "medium"
        return "low"

    def _merge_name(self, new_name: str, source: str):
        old = self.data.get("canonical_name", "")
        if not old:
            self.data["canonical_name"] = new_name
            return
        if source in ("tianyancha", "qichacha") and new_name != old:
            self.data.setdefault("aliases", []).append(old)
            self.data["canonical_name"] = new_name

    def _merge_aliases(self, new_aliases: List[str]):
        if not isinstance(new_aliases, list):
            return
        canonical = self.data.get("canonical_name", "")
        existing = set(self.data.get("aliases", []))
        for alias in new_aliases:
            if alias and alias != canonical and alias not in existing:
                existing.add(alias)
        self.data["aliases"] = sorted(existing)
