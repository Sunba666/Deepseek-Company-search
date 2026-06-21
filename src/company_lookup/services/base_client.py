# -*- coding: utf-8 -*-
"""
API客户端基类 - 包含熔断机制和通用功能
"""

import os
import time
import asyncio
import requests
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime
from dataclasses import asdict

from .dto import APIResponse, DataSource


class CircuitBreaker:
    """
    熔断器实现
    防止级联故障，当某个API持续失败时暂时禁用
    """

    def __init__(self, failure_threshold: int = 5, timeout: int = 60, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold  # 失败次数阈值
        self.timeout = timeout                     # 超时时间（秒）
        self.recovery_timeout = recovery_timeout   # 恢复超时（秒）

        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half_open

    def record_success(self):
        """记录成功调用"""
        self.failure_count = 0
        self.state = "closed"

    def record_failure(self):
        """记录失败调用"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"

    def can_attempt(self) -> bool:
        """检查是否可以尝试调用"""
        if self.state == "closed":
            return True

        if self.state == "open":
            if self.last_failure_time:
                elapsed = time.time() - self.last_failure_time
                if elapsed >= self.recovery_timeout:
                    self.state = "half_open"
                    return True
            return False

        # half_open 状态允许一次尝试
        return True

    def get_status(self) -> Dict[str, Any]:
        """获取熔断器状态"""
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time,
            "can_attempt": self.can_attempt()
        }


class BaseAPIClient(ABC):
    """
    API客户端基类
    提供统一的HTTP请求、错误处理、缓存、熔断机制
    """

    def __init__(
        self,
        name: str,
        source: DataSource,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30
    ):
        self.name = name
        self.source = source
        self.api_key = api_key or self._get_env_key()
        self.base_url = base_url or self._get_base_url()
        self.timeout = timeout
        self.circuit_breaker = CircuitBreaker()
        self._session: Optional[requests.Session] = None

    @property
    def session(self) -> requests.Session:
        """延迟创建 Session（避免未关闭的 Session 泄漏）。"""
        if self._session is None:
            self._session = requests.Session()
        return self._session

    def __del__(self):
        if self._session is not None:
            self._session.close()

    def _get_env_key(self) -> Optional[str]:
        """从环境变量获取API密钥"""
        env_key_map = {
            "tianyacha": "TIANYACHA_API_KEY",
            "qichacha": "QICHACHA_API_KEY",
            "tavily": "TAVILY_API_KEY",
            "bing_news": "BING_API_KEY",
            "wenshu": "WENSHU_API_KEY",
            "qixinbao": "QIXINBAO_API_KEY"
        }
        key_name = env_key_map.get(self.source.value)
        if key_name:
            return os.getenv(key_name)
        return None

    def _get_base_url(self) -> Optional[str]:
        """获取API基础URL"""
        return None

    def is_available(self) -> bool:
        """检查API是否可用（已配置密钥且熔断器允许）"""
        return self.api_key is not None and self.circuit_breaker.can_attempt()

    def is_configured(self) -> bool:
        """检查API是否已配置"""
        return self.api_key is not None

    def _make_request(
        self,
        method: str,
        url: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        **kwargs
    ) -> APIResponse:
        """
        发起HTTP请求
        包含熔断器保护和统一错误处理
        """
        start_time = time.time()

        if not self.circuit_breaker.can_attempt():
            return APIResponse(
                success=False,
                error=f"{self.name} 熔断器已触发，暂时不可用",
                source=self.source
            )

        try:
            full_url = f"{self.base_url}{url}" if self.base_url else url

            # 构建请求头
            request_headers = self._get_headers()
            if headers:
                request_headers.update(headers)

            response = self.session.request(
                method=method,
                url=full_url,
                params=params,
                json=data,
                headers=request_headers,
                timeout=self.timeout,
                **kwargs
            )

            elapsed = time.time() - start_time

            if response.status_code == 200:
                self.circuit_breaker.record_success()
                return APIResponse(
                    success=True,
                    data=response.json(),
                    source=self.source,
                    fetch_time=datetime.now().isoformat()
                )
            else:
                self.circuit_breaker.record_failure()
                return APIResponse(
                    success=False,
                    error=f"HTTP {response.status_code}: {response.text[:200]}",
                    source=self.source
                )

        except requests.exceptions.Timeout:
            self.circuit_breaker.record_failure()
            return APIResponse(
                success=False,
                error=f"{self.name} 请求超时（{self.timeout}秒）",
                source=self.source
            )

        except requests.exceptions.RequestException as e:
            self.circuit_breaker.record_failure()
            return APIResponse(
                success=False,
                error=f"{self.name} 请求失败: {str(e)}",
                source=self.source
            )

        except Exception as e:
            self.circuit_breaker.record_failure()
            return APIResponse(
                success=False,
                error=f"{self.name} 未知错误: {str(e)}",
                source=self.source
            )

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    @abstractmethod
    def search(self, query: str, **kwargs) -> APIResponse:
        """搜索接口（子类必须实现）"""
        pass

    def get_status(self) -> Dict[str, Any]:
        """获取API状态"""
        return {
            "name": self.name,
            "source": self.source.value,
            "configured": self.is_configured(),
            "available": self.is_available(),
            "circuit_breaker": self.circuit_breaker.get_status()
        }


class AsyncBaseAPIClient(ABC):
    """
    异步API客户端基类
    支持asyncio并发调用
    """

    def __init__(
        self,
        name: str,
        source: DataSource,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30
    ):
        self.name = name
        self.source = source
        self.api_key = api_key or self._get_env_key()
        self.base_url = base_url or self._get_base_url()
        self.timeout = timeout
        self.circuit_breaker = CircuitBreaker()

    def _get_env_key(self) -> Optional[str]:
        """从环境变量获取API密钥"""
        return None

    def _get_base_url(self) -> Optional[str]:
        """获取API基础URL"""
        return None

    def is_available(self) -> bool:
        """检查API是否可用"""
        return self.api_key is not None and self.circuit_breaker.can_attempt()

    def is_configured(self) -> bool:
        """检查API是否已配置"""
        return self.api_key is not None

    async def _async_request(
        self,
        method: str,
        url: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        **kwargs
    ) -> APIResponse:
        """异步发起HTTP请求"""
        import aiohttp

        start_time = time.time()

        if not self.circuit_breaker.can_attempt():
            return APIResponse(
                success=False,
                error=f"{self.name} 熔断器已触发，暂时不可用",
                source=self.source
            )

        try:
            full_url = f"{self.base_url}{url}" if self.base_url else url

            request_headers = self._get_headers()
            if headers:
                request_headers.update(headers)

            timeout_obj = aiohttp.ClientTimeout(total=self.timeout)

            async with aiohttp.ClientSession(timeout=timeout_obj) as session:
                async with session.request(
                    method=method,
                    url=full_url,
                    params=params,
                    json=data,
                    headers=request_headers,
                    **kwargs
                ) as response:
                    elapsed = time.time() - start_time

                    if response.status == 200:
                        self.circuit_breaker.record_success()
                        json_data = await response.json()
                        return APIResponse(
                            success=True,
                            data=json_data,
                            source=self.source,
                            fetch_time=datetime.now().isoformat()
                        )
                    else:
                        self.circuit_breaker.record_failure()
                        text = await response.text()
                        return APIResponse(
                            success=False,
                            error=f"HTTP {response.status}: {text[:200]}",
                            source=self.source
                        )

        except asyncio.TimeoutError:
            self.circuit_breaker.record_failure()
            return APIResponse(
                success=False,
                error=f"{self.name} 请求超时（{self.timeout}秒）",
                source=self.source
            )

        except aiohttp.ClientError as e:
            self.circuit_breaker.record_failure()
            return APIResponse(
                success=False,
                error=f"{self.name} 请求失败: {str(e)}",
                source=self.source
            )

        except Exception as e:
            self.circuit_breaker.record_failure()
            return APIResponse(
                success=False,
                error=f"{self.name} 未知错误: {str(e)}",
                source=self.source
            )

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    @abstractmethod
    async def search(self, query: str, **kwargs) -> APIResponse:
        """搜索接口（子类必须实现）"""
        pass

    def get_status(self) -> Dict[str, Any]:
        """获取API状态"""
        return {
            "name": self.name,
            "source": self.source.value,
            "configured": self.is_configured(),
            "available": self.is_available(),
            "circuit_breaker": self.circuit_breaker.get_status()
        }
