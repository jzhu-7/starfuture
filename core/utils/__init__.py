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
from ..config import HEADERS, get_project_config, REQUEST_TIMEOUT

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

def get_buildings_url(project: str = 'house') -> Dict[str, str]:
    """获取楼栋URL映射（按项目）
    project: 'house' 或 'warehouse'
    """
    cfg = get_project_config(project)
    target_url = cfg.get('TARGET_URL')
    base_url = cfg.get('BASE_URL')

    html = fetch_html(target_url)
    soup = BeautifulSoup(html, "html.parser")

    buildings = {}

    for a in soup.find_all("a", href=True):
        href = a["href"]
        name = a.get_text(strip=True)

        # 只筛选"楼栋链接"（保留原有筛选逻辑，如需支持仓储项目请根据需要调整条件）
        if (
            "pageId=320833" in href
            and "buildingId=" in href
            and "salePermitId=" in href
            and name.endswith("住宅楼")
        ):
            full_url = urljoin(base_url, href)
            full_url = full_url.replace("https://", "http://", 1)
            buildings[name] = full_url

    return buildings

def safe_delay(seconds: float = 0.3):
    """安全延迟"""
    time.sleep(seconds)