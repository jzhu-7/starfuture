"""
配置管理模块（支持多项目/多数据目录）
"""
import os
from typing import Dict

# 默认项目类型（可通过环境变量覆盖）
DEFAULT_PROJECT = os.environ.get("PROJECT_TYPE", "house")  # 'house' 或 'warehouse'

# 各项目的抓取 URL 等配置
PROJECTS = {
    "house": {
        "BASE_URL": "https://bjjs.zjw.beijing.gov.cn",
        "TARGET_URL": (
            "http://bjjs.zjw.beijing.gov.cn/eportal/ui?"
            "pageId=411612&systemId=2&srcId=1&id=8017587&rowcount=16"
        ),
        "DATA_URL": "http://bjjs.zjw.beijing.gov.cn/eportal/ui?pageId=320794&projectID=8017587&systemID=2&srcId=1",
    },
    "warehouse": {
        "BASE_URL": "https://bjjs.zjw.beijing.gov.cn",
        "TARGET_URL": (
            "http://bjjs.zjw.beijing.gov.cn/eportal/ui?"
            "pageId=411612&systemId=2&srcId=1&id=8083301&rowcount=18"
        ),
        "DATA_URL": "http://bjjs.zjw.beijing.gov.cn/eportal/ui?pageId=320794&projectID=8083301&systemID=2&srcId=1",
    }
}

# 请求头配置
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}

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


def get_project_config(project: str = None) -> Dict:
    """返回指定项目的运行时配置，包括文件路径等"""
    project = project or DEFAULT_PROJECT
    if project not in PROJECTS:
        raise ValueError(f"未知的项目: {project}")

    base = PROJECTS[project].copy()
    data_dir = os.path.join("data", project)
    base["DATA_DIR"] = data_dir
    base["AREAS_FILE"] = os.path.join(data_dir, "areas", "areas.json")
    base["TOTAL_FILE"] = os.path.join(data_dir, "total.json")
    base["SALES_DIR"] = os.path.join(data_dir, "sales")
    return base