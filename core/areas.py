import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import re
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# =========================
# 基本配置
# =========================
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


HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"
}

OUTPUT_FILE = "data/areas/areas.json"  # Change output file to .json


# =========================
# 1️⃣ 提取楼盘表页中的房号链接
# =========================
def extract_house_links(html):
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


# =========================
# 2️⃣ 提取单元号详情页中的建筑面积
# =========================
def extract_build_area(html):
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


# =========================
# 3️⃣ 处理单个楼栋的房源信息
# =========================
def process_building_data(bid, url):
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

                building_data.append({
                    "house_no": h["house_no"],
                    "area": area
                })

                time.sleep(0.3)  # 防止请求过快
            except Exception as e:
                print(f"❌ {h['house_no']} 解析失败：{e}")

        return bid, building_data
    except Exception as e:
        print(f"❌ 请求楼盘页面失败：{e}")
        return bid, []


# =========================
# 4️⃣ 主流程
# =========================
def main():
    data = {}

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_building_data, bid, url): bid for bid, url in BUILDING_URLS.items()}
        
        for future in as_completed(futures):
            bid, building_data = future.result()

            if building_data:
                data[bid] = {
                    "building_name": bid,
                    "house_data": building_data
                }

    # =========================
    # 5️⃣ 导出 JSON
    # =========================
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"✅ 已导出数据到 {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
