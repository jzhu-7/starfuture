"""
数据处理模块
负责数据更新、计算和整合逻辑
"""
import os
import json
import requests
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup

from config import DATA_URL, HEADERS, TOTAL_FILE, AREAS_FILE
from utils import fetch_html
from scrapers.status_scraper import get_status_changes
from models import SalesStats, StatusChange

logger = logging.getLogger(__name__)

def read_json_as_dict(json_file: str) -> Dict[str, Dict]:
    """以日期为key读取JSON"""
    if not os.path.exists(json_file):
        return {}

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        return {item["日期"]: item for item in data}

def write_json(data_by_date: Dict[str, Dict], json_file: str):
    """写入JSON文件"""
    data_list = [data_by_date[d] for d in sorted(data_by_date.keys())]
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data_list, f, ensure_ascii=False, indent=4)

def find_base_record(data_by_date: Dict[str, Dict], today: str) -> Optional[Dict]:
    """找到用于对比的上一条记录"""
    dates = sorted(data_by_date.keys())
    if not dates:
        return None

    if dates[-1] != today:
        return data_by_date[dates[-1]]

    if len(dates) >= 2:
        return data_by_date[dates[-2]]

    return None

def parse_presale_contract_stats(html: str) -> Optional[SalesStats]:
    """解析期房签约统计数据"""
    soup = BeautifulSoup(html, "html.parser")

    title_td = soup.find(
        lambda tag: tag.name == "td" and "期房签约统计" in tag.get_text()
    )
    if not title_td:
        return None

    outer_table = title_td.find_parent("table")
    data_table = outer_table.find_all("table")[0]

    rows = data_table.find_all("tr")
    headers = [td.get_text(strip=True) for td in rows[0].find_all("td")]
    values = [td.get_text(strip=True) for td in rows[1].find_all("td")]
    data = dict(zip(headers, values))

    return SalesStats(
        signed_units=int(data.get("已签约套数", 0)),
        signed_area=float(data.get("已签约面积(M2)", "0")),
        avg_price=float(data.get("成交均价(￥/M2)", "0")),
    )

def build_house_area_map() -> Dict[str, Dict[str, float]]:
    """构建房源面积映射"""
    if not os.path.exists(AREAS_FILE):
        raise FileNotFoundError(f"面积数据文件不存在: {AREAS_FILE}")

    with open(AREAS_FILE, 'r', encoding='utf-8') as f:
        areas_data = json.load(f)

    house_area_map = {}
    for building, bdata in areas_data.items():
        house_area_map[building] = {h["house_no"]: h["area"] for h in bdata["house_data"]}

    return house_area_map

def calculate_incremental_data(stats: SalesStats, base_record: Optional[Dict]) -> Tuple[float, str, str]:
    """计算增量数据"""
    cur_area = stats.signed_area
    cur_price = stats.avg_price

    # 基准数据
    prev_area = float(base_record["已签约面积(M2)"]) if base_record else 0.0
    prev_price = float(base_record["成交均价(￥/M2)"]) if base_record else 0.0
    prev_total = prev_area * prev_price

    # 增量计算
    delta_area = round(cur_area - prev_area, 2)

    if delta_area > 0:
        cur_total = cur_area * cur_price
        delta_total = round(cur_total - prev_total, 2)
        delta_unit = round(delta_total / delta_area, 2)
    else:
        delta_total = ""
        delta_unit = ""

    return delta_area, delta_total, delta_unit

def process_status_changes(changes: List[StatusChange], house_area_map: Dict[str, Dict[str, float]]) -> List[Dict]:
    """处理状态变化，添加面积信息"""
    processed_changes = []

    for change in changes:
        if change.prev_status == "可售":
            building_name = change.building_name
            house_no = change.house_no

            area = house_area_map.get(building_name, {}).get(house_no, 0.0)

            processed_changes.append({
                "building_name": building_name,
                "house_no": house_no,
                "area": area
            })

    return processed_changes

def update_sales_data() -> bool:
    """主数据更新流程"""
    try:
        # 构建房源面积映射
        house_area_map = build_house_area_map()

        today = datetime.now().strftime("%Y-%m-%d")

        logger.info("🌐 请求页面...")
        resp = requests.get(DATA_URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        resp.encoding = "utf-8"

        stats = parse_presale_contract_stats(resp.text)
        if not stats:
            logger.error("❌ 未获取期房签约统计")
            return False

        data_by_date = read_json_as_dict(TOTAL_FILE)
        base_record = find_base_record(data_by_date, today)

        # 计算增量数据
        delta_area, delta_total, delta_unit = calculate_incremental_data(stats, base_record)

        # 写入当天数据
        data_by_date[today] = {
            "日期": today,
            "已签约套数": stats.signed_units,
            "已签约面积(M2)": round(stats.signed_area, 2),
            "成交均价(￥/M2)": round(stats.avg_price, 2),
            "成交户号": [],  # 初始化为空列表
            "面积(M2)": delta_area if delta_area > 0 else "",
            "总价(￥)": delta_total,
            "均价(￥/M2)": delta_unit,
        }

        # 如果有新数据，处理状态变化
        if delta_area > 0:
            changes = get_status_changes()
            if changes:
                processed_changes = process_status_changes(changes, house_area_map)
                data_by_date[today]["成交户号"] = processed_changes

        # 重写JSON文件
        write_json(data_by_date, TOTAL_FILE)

        logger.info(f"✅ {today} 数据已写入（同日自动覆盖）")
        return True

    except Exception as e:
        logger.error(f"❌ 数据更新失败: {e}")
        return False