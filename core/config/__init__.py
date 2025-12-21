"""
配置管理模块
集中管理所有配置项
"""
import os
from typing import Dict

# 基础URL配置
BASE_URL = "https://bjjs.zjw.beijing.gov.cn"
TARGET_URL = (
    "http://bjjs.zjw.beijing.gov.cn/eportal/ui?"
    "pageId=411612&systemId=2&srcId=1&id=8017587&rowcount=16"
)
DATA_URL = "http://bjjs.zjw.beijing.gov.cn/eportal/ui?pageId=320794&projectID=8017587&systemID=2&srcId=1"

# 请求头配置
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}

# 数据文件路径
DATA_DIR = "data"
AREAS_FILE = os.path.join(DATA_DIR, "areas", "areas.json")
TOTAL_FILE = os.path.join(DATA_DIR, "total.json")
SALES_DIR = os.path.join(DATA_DIR, "sales")

# 状态颜色映射
COLOR_STATUS_MAP = {
    "#CCCCCC": "不可售",
    "#33CC00": "可售",
    "#FFCC99": "已预订",
    "#FF0000": "已签约",
    "#FFFF00": "已办理预售项目抵押",
    "#D2691E": "网上联机备案",
    "#00FFFF": "资格核验中",
}

ALL_STATUS = list(COLOR_STATUS_MAP.values())

# 并发配置
MAX_WORKERS = 5

# 请求超时配置
REQUEST_TIMEOUT = 30

# 延迟配置（秒）
REQUEST_DELAY = 0.3