# -*- coding: utf-8 -*-
"""
BaseEngine — 后台守护引擎基类。

封装四个引擎共享的线程生命周期管理：
- start/stop/is_running/status
- 指数退避崩溃恢复
- 心跳标记 last_heartbeat
- _stats 字典统一字段

子类只需实现 _run_loop()，并在循环体外套用
try/except 调用 self._handle_crash(e)。
"""
import logging
import threading
import time
from datetime import datetime
from typing import Dict, Optional


class BaseEngine:
    """后台守护引擎基类。"""

    def __init__(self, name: str):
        """
        :param name: 引擎名称（用于日志前缀、状态标识）。
        """
        self._name = name
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._stats: Dict = {
            "is_running": False,
            "started_at": None,
            "last_heartbeat": None,
            "crash_count": 0,
            "last_error": None,
        }
        self._logger = logging.getLogger(__name__)

    # ═══════════════════════════════════════════════
    #  公共接口
    # ═══════════════════════════════════════════════

    def start(self):
        if self.is_running():
            self._logger.info(f"[{self._name}] 已在运行中")
            return
        self._stop_event.clear()
        self._stats["started_at"] = datetime.now().isoformat()
        self._stats["is_running"] = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self._logger.info(f"[{self._name}] ✅ 引擎已启动")

    def stop(self):
        if not self.is_running():
            return
        self._stop_event.set()
        self._stats["is_running"] = False
        self._logger.info(f"[{self._name}] ⏹ 引擎已停止")

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def status(self) -> Dict:
        s = dict(self._stats)
        s["is_running"] = self.is_running()
        return s

    # ═══════════════════════════════════════════════
    #  子类工具方法
    # ═══════════════════════════════════════════════

    def _handle_crash(self, e: Exception):
        """崩溃处理：日志 + 指数退避休眠。"""
        self._logger.exception(f"[{self._name}] 主循环异常: {e}")
        self._stats["last_error"] = f"{type(e).__name__}: {e}"
        self._stats["crash_count"] = self._stats.get("crash_count", 0) + 1
        crash_count = self._stats["crash_count"]
        backoff = min(10 * 3 ** (crash_count - 1), 300)
        self._logger.warning(f"[{self._name}] 第 {crash_count} 次崩溃，{backoff}s 后重试")
        self._stop_event.wait(backoff)

    def _heartbeat(self):
        """记录心跳时间戳。"""
        self._stats["last_heartbeat"] = datetime.now().isoformat()

    def _run_loop(self):
        """主循环 — 子类必须覆盖。"""
        raise NotImplementedError
