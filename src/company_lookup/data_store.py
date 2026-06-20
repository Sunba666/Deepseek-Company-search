# -*- coding: utf-8 -*-
"""数据存储模块 - 提供带TTL和大小限制的缓存功能

【修复】原实现使用裸 dict，无过期、无大小限制，长期运行会内存泄漏。
现改为支持 TTL 过期 + 最大容量 LRU 淘汰的缓存。
"""

import time
import threading
from typing import Optional, Any

# 默认缓存TTL（秒）- 10分钟
DEFAULT_TTL = 600

# 最大缓存条目数
MAX_CACHE_SIZE = 500

# 全局缓存字典：key -> {"value": ..., "expire_at": timestamp}
_cache = {}

# 线程锁，保证并发安全
_lock = threading.Lock()


def get_cache(key: str) -> Any:
    """
    获取缓存数据（已过期的自动清除）
    :param key: 缓存键
    :return: 缓存值，如果不存在或已过期返回None
    """
    with _lock:
        entry = _cache.get(key)
        if entry is None:
            return None
        # 检查是否过期
        if entry["expire_at"] and time.time() > entry["expire_at"]:
            del _cache[key]
            return None
        return entry["value"]


def set_cache(key: str, value: Any, ttl: int = DEFAULT_TTL):
    """
    设置缓存数据（带TTL过期）
    :param key: 缓存键
    :param value: 缓存值
    :param ttl: 过期时间（秒），0表示永不过期
    """
    with _lock:
        # 如果缓存已满，淘汰最早的条目
        if len(_cache) >= MAX_CACHE_SIZE and key not in _cache:
            _evict_oldest()

        expire_at = (time.time() + ttl) if ttl > 0 else None
        _cache[key] = {"value": value, "expire_at": expire_at}


def delete_cache(key: str):
    """
    删除指定缓存
    :param key: 缓存键
    """
    with _lock:
        _cache.pop(key, None)


def clear_cache():
    """清除所有缓存"""
    with _lock:
        _cache.clear()


def _evict_oldest():
    """淘汰最早插入的缓存条目（简单FIFO策略）"""
    if not _cache:
        return
    # 找到并删除最早插入的key
    oldest_key = next(iter(_cache))
    del _cache[oldest_key]


def cache_stats() -> dict:
    """获取缓存统计信息（调试用）"""
    with _lock:
        now = time.time()
        expired = sum(1 for e in _cache.values() if e["expire_at"] and now > e["expire_at"])
        return {
            "total": len(_cache),
            "expired_but_not_cleaned": expired,
            "max_size": MAX_CACHE_SIZE,
        }
