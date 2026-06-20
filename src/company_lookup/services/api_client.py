# -*- coding: utf-8 -*-
"""
统一 API 调用工具：重试、超时、降级、日志。
"""
import time
import logging
import asyncio
from functools import wraps
from typing import Callable, Type, Tuple, Optional

logger = logging.getLogger(__name__)

# 全局超时配置（秒）
HTTP_TIMEOUT = (10, 15)  # (connect_timeout, read_timeout)
API_TIMEOUT = 25         # 整个 API 调用的硬超时


def retry_on_failure(
    max_retries: int = 2,
    delay: float = 1.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    api_name: str = "",
):
    """
    重试装饰器：失败后自动重试，指数退避。
    用法：
        @retry_on_failure(api_name="DeepSeek")
        def call_deepseek(...):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(max_retries + 1):
                try:
                    start = time.time()
                    result = func(*args, **kwargs)
                    elapsed = time.time() - start
                    if attempt > 0:
                        logger.info(
                            f"{api_name or func.__name__} 第 {attempt + 1} 次重试成功 "
                            f"(耗时 {elapsed:.1f}s)"
                        )
                    return result
                except exceptions as e:
                    last_exc = e
                    elapsed = time.time() - start if 'start' in dir() else 0
                    if attempt < max_retries:
                        wait = delay * (2 ** attempt)
                        logger.warning(
                            f"{api_name or func.__name__} 第 {attempt + 1} 次失败 "
                            f"(耗时 {elapsed:.1f}s): {e}，{wait:.1f}s 后重试"
                        )
                        time.sleep(wait)
                    else:
                        logger.error(
                            f"{api_name or func.__name__} 重试 {max_retries} 次后仍失败: {e}"
                        )
            raise last_exc
        return wrapper
    return decorator


def async_retry_on_failure(
    max_retries: int = 2,
    delay: float = 1.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    api_name: str = "",
):
    """异步版重试装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(max_retries + 1):
                try:
                    start = time.time()
                    result = await func(*args, **kwargs)
                    elapsed = time.time() - start
                    if attempt > 0:
                        logger.info(
                            f"{api_name or func.__name__} 第 {attempt + 1} 次重试成功 "
                            f"(耗时 {elapsed:.1f}s)"
                        )
                    return result
                except exceptions as e:
                    last_exc = e
                    if attempt < max_retries:
                        wait = delay * (2 ** attempt)
                        logger.warning(
                            f"{api_name or func.__name__} 第 {attempt + 1} 次失败: {e}，"
                            f"{wait:.1f}s 后重试"
                        )
                        await asyncio.sleep(wait)
                    else:
                        logger.error(
                            f"{api_name or func.__name__} 重试 {max_retries} 次后仍失败: {e}"
                        )
            raise last_exc
        return wrapper
    return decorator


def log_api_call(func: Callable):
    """记录 API 调用的入参、耗时和结果"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            logger.info(
                f"[API] {func.__name__} 成功 (耗时 {elapsed:.1f}s)"
            )
            return result
        except Exception as e:
            elapsed = time.time() - start
            logger.error(
                f"[API] {func.__name__} 失败 (耗时 {elapsed:.1f}s): {e}",
                exc_info=True
            )
            raise
    return wrapper
