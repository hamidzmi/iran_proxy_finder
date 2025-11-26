import re
from typing import List

import requests
from bs4 import BeautifulSoup

SOURCES = [
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&country=IR&timeout=10000&simplified=true",
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=https&country=IR&timeout=10000&simplified=true",
    "https://www.proxy-list.download/api/v1/get?type=http&country=IR",
    "https://www.proxy-list.download/api/v1/get?type=https&country=IR",
    "https://spys.one/free-proxy-list/IR/",
    "https://www.freeproxy.world/?country=IR",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
]


def fetch_proxy_page(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    return response.text


def extract_proxies(html: str) -> List[str]:
    soup = BeautifulSoup(html, "lxml")
    text_content = soup.get_text(" ")
    ip_port_pattern = re.compile(
        r"\b(?:(?:25[0-5]|2[0-4][0-9]|1\d{2}|[1-9]?\d)\.){3}"
        r"(?:25[0-5]|2[0-4][0-9]|1\d{2}|[1-9]?\d):\d+\b"
    )

    seen = set()
    proxies: List[str] = []

    for match in ip_port_pattern.finditer(text_content):
        proxy = match.group(0)
        if proxy not in seen:
            seen.add(proxy)
            proxies.append(proxy)

    if not proxies:
        proxy_cells = soup.find_all("td")
        for cell in proxy_cells:
            cell_text = cell.get_text(strip=True)
            match = ip_port_pattern.search(cell_text)
            if match:
                proxy = match.group(0)
                if proxy not in seen:
                    seen.add(proxy)
                    proxies.append(proxy)

    return proxies


def extract_freeproxy_world(html: str) -> List[str]:
    soup = BeautifulSoup(html, "lxml")
    ip_pattern = re.compile(
        r"\b(?:(?:25[0-5]|2[0-4][0-9]|1\d{2}|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4][0-9]|1\d{2}|[1-9]?\d)\b"
    )
    results: List[str] = []
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        for i, td in enumerate(tds):
            text = td.get_text(" ", strip=True)
            ip_match = ip_pattern.search(text)
            if ip_match:
                ip = ip_match.group(0)
                port = None
                if i + 1 < len(tds):
                    port_text = tds[i + 1].get_text(" ", strip=True)
                    port_match = re.search(r"\b\d{2,5}\b", port_text)
                    if port_match:
                        port = port_match.group(0)
                if port:
                    results.append(f"{ip}:{port}")
                break
    return results


def get_proxies() -> List[str]:
    all_proxies: List[str] = []
    seen = set()
    for url in SOURCES:
        try:
            html = fetch_proxy_page(url)
        except requests.RequestException as exc:
            print(f"Failed to fetch from {url}: {exc}")
            continue

        if "freeproxy.world" in url:
            extracted = extract_freeproxy_world(html)
            for proxy in extracted:
                if proxy not in seen:
                    seen.add(proxy)
                    all_proxies.append(proxy)
        elif (
            "displayproxies" in url
            or "/api/v1/get" in url
            or "raw.githubusercontent.com" in url
        ):
            lines = [line.strip() for line in html.splitlines() if line.strip()]
            for line in lines:
                if ":" in line and line not in seen:
                    seen.add(line)
                    all_proxies.append(line)
        else:
            extracted = extract_proxies(html)
            for proxy in extracted:
                if proxy not in seen:
                    seen.add(proxy)
                    all_proxies.append(proxy)

    print(f"Extracted {len(all_proxies)} unique proxies.")
    return all_proxies


__all__ = ["get_proxies"]
