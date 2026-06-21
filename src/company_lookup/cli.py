import os
import sys
import webbrowser
import threading
import requests

# 设置标准输出编码为UTF-8
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from . import __version__
from .app import create_app

def check_update():
    try:
        current = __version__
        resp = requests.get("https://pypi.org/pypi/company-lookup/json", timeout=2)
        latest = resp.json()["info"]["version"]
        if latest != current:
            try:
                print(f"[UPDATE] Version {latest} available. Run `pip install --upgrade company-lookup` to upgrade.")
            except Exception:
                pass
    except Exception:
        pass

def main():
    port = int(os.getenv("PORT", 5000))
    url = f"http://127.0.0.1:{port}"

    # 延迟1.5秒后自动打开浏览器
    threading.Timer(1.5, lambda: webbrowser.open(url)).start()

    check_update()
    try:
        print(f"[INFO] Company Lookup AI started at {url}")
    except Exception:
        pass
    create_app().run(host="127.0.0.1", port=port, debug=False)
