import os
import time
from typing import Tuple

import requests

DEFAULT_TARGET = os.environ.get("TARGET_URL", "https://ib.tejaratbank.ir/")
VERIFY_IR = os.environ.get("VERIFY_IR") == "1"


def test_proxy(proxy: str, target_url: str | None = None) -> Tuple[bool, float | None, str | None]:
    for scheme in ("http", "https"):
        proxies = {
            "http": f"{scheme}://{proxy}",
            "https": f"{scheme}://{proxy}",
        }
        try:
            start = time.monotonic()
            response = requests.get(target_url or DEFAULT_TARGET, proxies=proxies, timeout=8, verify=False)
            latency = time.monotonic() - start
            if 200 <= response.status_code < 400:
                if VERIFY_IR:
                    try:
                        geo = requests.get("https://ipapi.co/json", proxies=proxies, timeout=6, verify=False)
                        if geo.ok:
                            data = geo.json()
                            if str(data.get("country_code")) != "IR":
                                continue
                    except requests.RequestException:
                        continue
                return True, latency, scheme
        except requests.RequestException:
            pass
    return False, None, None


__all__ = ["test_proxy"]
