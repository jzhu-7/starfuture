"""
主入口模块
统一的数据更新入口
"""
import logging
from processors.data_processor import update_sales_data
from scrapers.area_scraper import scrape_areas_data

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def update_data():
    """更新销售数据"""
    print("🚀 开始更新销售数据...")
    success = update_sales_data()
    if success:
        print("✅ 数据更新完成")
    else:
        print("❌ 数据更新失败")

def update_areas():
    """更新面积数据"""
    print("🚀 开始更新面积数据...")
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(__file__))
        from scrapers.area_scraper import scrape_areas_data
        scrape_areas_data()
        print("✅ 面积数据更新完成")
    except Exception as e:
        print(f"❌ 面积数据更新失败: {e}")

def main():
    """主函数"""
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "areas":
            update_areas()
        elif command == "data":
            update_data()
        else:
            print("用法: PYTHONPATH=/path/to/core python3 core/main.py [areas|data]")
    else:
        # 默认更新数据
        update_data()

if __name__ == "__main__":
    main()