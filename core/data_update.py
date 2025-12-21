import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
from typing import Dict, Optional
from house_status import get_status_changes
import re
import json

URL = "http://bjjs.zjw.beijing.gov.cn/eportal/ui?pageId=320794&projectID=8017587&systemID=2&srcId=1"
JSON_FILE = "data/total.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ==================================================
# 工具函数
# ==================================================

def read_json_as_dict(json_file: str) -> Dict[str, Dict]:
    """
    以 日期 为 key 读取 JSON
    """
    if not os.path.exists(json_file):
        return {}

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        return {item["日期"]: item for item in data}


def write_json(data_by_date: Dict[str, Dict], json_file: str):
    """
    写入 JSON 文件
    """
    data_list = [data_by_date[d] for d in sorted(data_by_date.keys())]
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data_list, f, ensure_ascii=False, indent=4)


def find_base_record(data_by_date: Dict[str, Dict], today: str) -> Optional[Dict]:
    """
    找到用于对比的上一条记录
    """
    dates = sorted(data_by_date.keys())
    if not dates:
        return None

    if dates[-1] != today:
        return data_by_date[dates[-1]]

    if len(dates) >= 2:
        return data_by_date[dates[-2]]

    return None


# ==================================================
# 页面解析
# ==================================================

def parse_presale_contract_stats(html: str) -> Optional[Dict]:
    """
    解析「期房签约统计」累计数据
    """
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

    return {
        "已签约套数": int(data.get("已签约套数", 0)),
        "已签约面积": float(data.get("已签约面积(M2)", "0")),
        "成交均价": float(data.get("成交均价(￥/M2)", "0")),
    }


# ==================================================
# 主流程
# ==================================================

def main():
    with open("data/areas/areas.json", 'r', encoding='utf-8') as f:
        areas_data = json.load(f)

    # 构建房源面积映射
    house_area_map = {}
    for building, bdata in areas_data.items():
        house_area_map[building] = {h["house_no"]: h["area"] for h in bdata["house_data"]}

    today = datetime.now().strftime("%Y-%m-%d")

    print("🌐 请求页面...")
    resp = requests.get(URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    resp.encoding = "utf-8"

    stats = parse_presale_contract_stats(resp.text)
    if not stats:
        print("❌ 未获取期房签约统计")
        return

    data_by_date = read_json_as_dict(JSON_FILE)
    base_record = find_base_record(data_by_date, today)

    # ===== 累计数据 =====
    cur_area = stats["已签约面积"]
    cur_price = stats["成交均价"]

    # ===== 基准数据 =====
    prev_area = float(base_record["已签约面积(M2)"]) if base_record else 0.0
    prev_price = float(base_record["成交均价(￥/M2)"]) if base_record else 0.0
    prev_total = prev_area * prev_price

    # ===== 增量计算 =====
    delta_area = round(cur_area - prev_area, 2)

    if delta_area > 0:
        cur_total = cur_area * cur_price
        delta_total = round(cur_total - prev_total, 2)
        delta_unit = round(delta_total / delta_area, 2)
    else:
        delta_total = ""
        delta_unit = ""

    # ===== 日志 =====
    # print("\n🧾 计算过程")
    # print(f"today       = {today}")
    # print(f"prev_area   = {prev_area}")
    # print(f"cur_area    = {cur_area}")
    # print(f"delta_area  = {delta_area}")

    # ===== 写入当天 =====
    data_by_date[today] = {
        "日期": today,
        "已签约套数": stats["已签约套数"],
        "已签约面积(M2)": round(cur_area, 2),
        "成交均价(￥/M2)": round(cur_price, 2),
        "成交户号": [],  # 初始化为空列表
        "面积(M2)": delta_area if delta_area > 0 else "",
        "总价(￥)": delta_total,
        "均价(￥/M2)": delta_unit,
    }

    # ===== 重写 JSON =====
    write_json(data_by_date, JSON_FILE)

    print(f"\n✅ {today} 数据已写入（同日自动覆盖）")

    # 如果有新数据，调用房屋状态更新程序
    if delta_area > 0:
        changes = get_status_changes()
        print(changes)
        if changes:
            data_by_date[today].setdefault("成交户号", [])
            for change in changes:
                if change["prev_status"] == "可售":
                    building_name = change["building_name"]
                    house_no = change["house_no"]

                    area = house_area_map.get(building_name, {}).get(house_no, 0.0)
                    print(f"🏠 {building_name} {house_no}，面积：{area}")

                    data_by_date[today]["成交户号"].append({
                        "building_name": building_name,
                        "house_no": house_no,
                        "area": area
                    })


            # 重新写入 JSON
            write_json(data_by_date, JSON_FILE)

if __name__ == "__main__":
    main()
