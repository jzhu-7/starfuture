"""
工具函数模块
包含通用工具函数
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import logging
from typing import Dict, Optional
from config import HEADERS, BASE_URL, TARGET_URL, REQUEST_TIMEOUT

logger = logging.getLogger(__name__)

def fetch_html(url: str, timeout: int = REQUEST_TIMEOUT) -> str:
    """获取网页HTML内容"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding
        return resp.text
    except Exception as e:
        logger.error(f"请求失败 {url}: {e}")
        raise

def get_buildings_url() -> Dict[str, str]:
    """获取楼栋URL映射"""
    html = fetch_html(TARGET_URL)
    soup = BeautifulSoup(html, "html.parser")

    buildings = {}

    for a in soup.find_all("a", href=True):
        href = a["href"]
        name = a.get_text(strip=True)

        # 只筛选"楼栋链接"
        if (
            "pageId=320833" in href
            and "buildingId=" in href
            and "salePermitId=" in href
            and name.endswith("住宅楼")
        ):
            full_url = urljoin(BASE_URL, href)
            full_url = full_url.replace("https://", "http://", 1)
            buildings[name] = full_url

    return buildings

def safe_delay(seconds: float = 0.3):
    """安全延迟"""
    time.sleep(seconds)