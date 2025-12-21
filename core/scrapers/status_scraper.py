"""
状态数据抓取模块
负责抓取房屋销售状态信息
"""
import os
import json
import re
import requests
import logging
from datetime import datetime
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple, Optional
from bs4 import BeautifulSoup

from config import HEADERS, SALES_DIR, COLOR_STATUS_MAP, MAX_WORKERS
from utils import fetch_html, get_buildings_url
from models import HouseData, BuildingData, StatusChange

logger = logging.getLogger(__name__)

def parse_status(style: str) -> str:
    """解析状态样式"""
    style = style.upper()
    for color, status in COLOR_STATUS_MAP.items():
        if color in style:
            return status
    return "其他"

def extract_building_name(soup) -> str:
    """提取楼栋名称"""
    span = soup.find("span", string=lambda x: x and "楼盘表" in x)
    if span:
        return span.get_text(strip=True).replace("楼盘表", "")
    return "未知楼栋"

def process_building(bid: str, url: str) -> Optional[BuildingData]:
    """处理单个楼栋"""
    logger.info(f"处理楼栋 {bid}...")

    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        resp.encoding = "utf-8"
    except Exception as e:
        logger.error(f"  ❌ 请求失败：{e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table", id="table_Buileing")
    if not table:
        logger.error("  ❌ 未找到 table_Buileing")
        return None

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

        rows.append(HouseData(
            house_no=house_no,
            status=status
        ))

        counter[status] += 1

    return BuildingData(
        building_name=bid,
        house_data=rows,
        status_count=dict(counter)
    )

def scrape_status_data() -> Dict[str, BuildingData]:
    """抓取所有楼栋状态数据"""
    BUILDING_URLS = get_buildings_url()
    all_buildings_data = {}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_building, bid, url)
                  for bid, url in BUILDING_URLS.items()]
        for future in as_completed(futures):
            building_data = future.result()
            if building_data:
                all_buildings_data[building_data.building_name] = building_data

    return all_buildings_data

def save_status_data(data: Dict[str, BuildingData], date: str):
    """保存状态数据到文件"""
    os.makedirs(SALES_DIR, exist_ok=True)
    json_path = os.path.join(SALES_DIR, f"{date}.json")

    # 转换为字典格式
    dict_data = {}
    for bid, bdata in data.items():
        dict_data[bid] = {
            "building_name": bdata.building_name,
            "house_data": [{"house_no": h.house_no, "status": h.status} for h in bdata.house_data],
            "status_count": bdata.status_count
        }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(dict_data, f, ensure_ascii=False, indent=2)

    logger.info(f"📄 已生成：{json_path}")
    return json_path

def compare_status_changes(prev_file: str, curr_file: str) -> List[StatusChange]:
    """比较状态变化"""
    changes = []

    # 读取前一天数据
    with open(prev_file, 'r', encoding='utf-8') as f:
        prev_data = json.load(f)

    # 读取当天数据
    with open(curr_file, 'r', encoding='utf-8') as f:
        curr_data = json.load(f)

    # 比较每个楼栋
    for building_name in curr_data:
        if building_name not in prev_data:
            logger.warning(f"跳过 {building_name}：前一天数据不存在")
            continue

        prev_building = prev_data[building_name]
        curr_building = curr_data[building_name]

        prev_houses = {h['house_no']: h['status'] for h in prev_building['house_data']}
        curr_houses = curr_building['house_data']

        for house in curr_houses:
            house_no = house['house_no']
            curr_status = house['status']
            prev_status = prev_houses.get(house_no, '不存在')

            if curr_status != prev_status:
                changes.append(StatusChange(
                    building_name=building_name,
                    house_no=house_no,
                    prev_status=prev_status,
                    curr_status=curr_status
                ))

    return changes

def get_latest_json_files() -> Tuple[str, str]:
    """获取最新的两个JSON文件"""
    if not os.path.exists(SALES_DIR):
        raise ValueError("data/sales 目录不存在")
    files = [f for f in os.listdir(SALES_DIR) if f.endswith('.json') and re.match(r'\d{4}-\d{2}-\d{2}\.json', f)]
    files.sort()
    if len(files) < 2:
        raise ValueError("至少需要两个JSON文件")
    return os.path.join(SALES_DIR, files[-2]), os.path.join(SALES_DIR, files[-1])

def get_status_changes() -> List[StatusChange]:
    """获取状态变化（完整流程）"""
    today = datetime.now().strftime("%Y-%m-%d")

    # 抓取并保存当天数据
    status_data = scrape_status_data()
    save_status_data(status_data, today)

    # 比较状态变化
    try:
        prev_file, curr_file = get_latest_json_files()
        changes = compare_status_changes(prev_file, curr_file)
        return changes
    except ValueError:
        # 如果没有足够的历史数据，返回空列表
        return []