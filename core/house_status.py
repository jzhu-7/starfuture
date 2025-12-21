import requests
from bs4 import BeautifulSoup
import csv
from collections import Counter
import time
from datetime import datetime
import os
import re
from urllib.parse import urljoin
import concurrent.futures
import json

# 自动识别最新的两个日期文件夹
def get_latest_dirs():
    dirs = [d for d in os.listdir('.') if os.path.isdir(d) and re.match(r'\d{4}-\d{2}-\d{2}', d)]
    dirs.sort()
    if len(dirs) < 2:
        raise ValueError("至少需要两个日期文件夹")
    return dirs[-2], dirs[-1]

# 配置路径

def compare_status_changes():
    PREV_DIR, CURR_DIR = get_latest_dirs()

    changes = []

    # 遍历当前目录的CSV文件（排除汇总文件）
    for file in os.listdir(CURR_DIR):
        if not file.endswith('.csv') or '汇总' in file:
            continue

        curr_path = os.path.join(CURR_DIR, file)
        prev_path = os.path.join(PREV_DIR, file)

        if not os.path.exists(prev_path):
            print(f"跳过 {file}：前一天文件不存在")
            continue

        # 读取前一天数据
        prev_data = {}
        with open(prev_path, newline='', encoding='utf-8-sig') as f:
            for row in csv.DictReader(f):
                prev_data[row['house_no']] = row['status']

        # 读取当天数据并比较
        with open(curr_path, newline='', encoding='utf-8-sig') as f:
            for row in csv.DictReader(f):
                house_no = row['house_no']
                curr_status = row['status']
                prev_status = prev_data.get(house_no, '不存在')

                if curr_status != prev_status:
                    changes.append({
                        'building': file.replace('.csv', ''),
                        'house_no': house_no,
                        'prev_status': prev_status,
                        'curr_status': curr_status
                    })
    # print(changes)
    return changes

# ==================================================
# 楼栋 URL 映射
# ==================================================
BASE_URL = "https://bjjs.zjw.beijing.gov.cn"
TARGET_URL = (
    "http://bjjs.zjw.beijing.gov.cn/eportal/ui?"
    "pageId=411612&systemId=2&srcId=1&id=8017587&rowcount=16"
)

def fetch_html(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers, timeout=10)
    resp.encoding = resp.apparent_encoding
    return resp.text

def get_buildings_url() -> str:
    html = fetch_html(TARGET_URL)
    soup = BeautifulSoup(html, "html.parser")

    buildings = {}

    for a in soup.find_all("a", href=True):
        href = a["href"]
        name = a.get_text(strip=True)

        # 只筛选“楼栋链接”
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

BUILDING_URLS = get_buildings_url()

# ==================================================
# 基本配置
# ==================================================
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

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

# ==================================================
# 工具函数
# ==================================================
def parse_status(style: str) -> str:
    style = style.upper()
    for color, status in COLOR_STATUS_MAP.items():
        if color in style:
            return status
    return "其他"

def extract_building_name(soup: BeautifulSoup) -> str:
    span = soup.find("span", string=lambda x: x and "楼盘表" in x)
    if span:
        return span.get_text(strip=True).replace("楼盘表", "")
    return "未知楼栋"

def safe_filename(name: str) -> str:
    return re.sub(r'[\\/:*?"<>|]', "_", name)

# ==================================================
# 并行处理函数
# ==================================================
def process_building(bid, url):
    print(f"\n处理楼栋 {bid}...")

    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        resp.encoding = "utf-8"
    except Exception as e:
        print(f"  ❌ 请求失败：{e}")
        return None, Counter(), 0, "失败"

    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table", id="table_Buileing")
    if not table:
        print("  ❌ 未找到 table_Buileing")
        return None, Counter(), 0, "失败"

    rows = []
    counter = Counter()

    for div in table.find_all("div"):
        style = div.get("style", "")
        if "BACKGROUND" not in style.upper():
            continue

        a = div.find("a")
        if not a:
            continue

        house_no = a.get_text(strip=True)
        status = parse_status(style)

        rows.append({
            "house_no": house_no,
            "status": status
        })

        counter[status] += 1

    # 单栋数据
    building_data = {
        "building_name": bid,
        "house_data": rows,
        "status_count": counter
    }

    return building_data

# ==================================================
# 主流程
# ==================================================
def get_status_changes():
    today = datetime.now().strftime("%Y-%m-%d")
    os.makedirs(today, exist_ok=True)

    # 楼栋级统计
    all_buildings_data = {}

    # 并行处理楼栋
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_building, bid, url) for bid, url in BUILDING_URLS.items()]
        for future in concurrent.futures.as_completed(futures):
            building_data = future.result()
            if building_data is None:
                continue
            all_buildings_data[building_data["building_name"]] = building_data

    # 保存数据到 JSON 文件
    json_path = os.path.join("data", f"{today}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_buildings_data, f, ensure_ascii=False, indent=2)

    print(f"\n📄 已生成：{json_path}")

    # 获取状态变化
    change = compare_status_changes()
    return change

# ==================================================
# 入口
# ==================================================
if __name__ == "__main__":
    get_status_changes()
