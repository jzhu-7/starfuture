"""
面积数据抓取模块
负责抓取楼栋和房源面积信息
"""
import json
import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from config import HEADERS, BASE_URL
from utils import fetch_html, get_buildings_url, safe_delay
from models import HouseData, BuildingData

def extract_house_links(html: str) -> List[Dict]:
    """提取房号链接"""
    soup = BeautifulSoup(html, "html.parser")
    houses = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        # 房号详情页的固定特征
        if "pageId=373432" in href and "houseId=" in href:
            house_no = a.get_text(strip=True)
            full_url = urljoin(BASE_URL, href)
            full_url = full_url.replace("https://", "http://", 1)
            houses.append({
                "house_no": house_no,
                "url": full_url
            })

    return houses

def extract_build_area(html: str) -> Optional[float]:
    """提取建筑面积"""
    soup = BeautifulSoup(html, "html.parser")

    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) == 2:
            left = tds[0].get_text(strip=True)
            if left == "建筑面积":
                right = tds[1].get_text(strip=True)
                m = re.search(r"([\d.]+)", right)
                if m:
                    return float(m.group(1))

    return None

def process_building_data(bid: str, url: str) -> Tuple[str, List[HouseData]]:
    """处理单个楼栋的房源信息"""
    print(f"🌐 正在请求楼盘表页面{bid} :{url}...")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.encoding = "utf-8"

        houses = extract_house_links(resp.text)
        print(f"🏠 共找到 {len(houses)} 套房源")

        building_data = []

        for idx, h in enumerate(houses, 1):
            print(f"[{idx}/{len(houses)}] 解析 {h['house_no']} ...")
            try:
                r = requests.get(h["url"], headers=HEADERS, timeout=10)
                r.encoding = "utf-8"
                area = extract_build_area(r.text)
                print(f"  建筑面积: {area} 平方米")
                if area is None:
                    print(f"❌ 未找到建筑面积")
                    continue

                building_data.append(HouseData(
                    house_no=h["house_no"],
                    area=area
                ))

                safe_delay()  # 防止请求过快
            except Exception as e:
                print(f"❌ {h['house_no']} 解析失败：{e}")

        return bid, building_data
    except Exception as e:
        print(f"❌ 请求楼盘页面失败：{e}")
        return bid, []

def scrape_areas_data(output_file: str = "data/areas/areas.json") -> Dict[str, BuildingData]:
    """主流程：抓取所有楼栋面积数据"""
    BUILDING_URLS = get_buildings_url()
    data = {}

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_building_data, bid, url): bid
                  for bid, url in BUILDING_URLS.items()}

        for future in as_completed(futures):
            bid, building_data = future.result()

            if building_data:
                data[bid] = BuildingData(
                    building_name=bid,
                    house_data=building_data
                )

    # 导出 JSON
    with open(output_file, "w", encoding="utf-8") as f:
        # 转换为字典格式以保持兼容性
        dict_data = {}
        for bid, bdata in data.items():
            dict_data[bid] = {
                "building_name": bdata.building_name,
                "house_data": [{"house_no": h.house_no, "area": h.area} for h in bdata.house_data]
            }
        json.dump(dict_data, f, ensure_ascii=False, indent=4)

    print(f"✅ 已导出数据到 {output_file}")
    return data