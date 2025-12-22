"""
主入口模块
统一的数据更新入口
"""
import logging
from processors.data_processor import update_sales_data

logger = logging.getLogger(__name__)

def update_data():
    """更新销售数据"""
    logger.info("🚀 开始更新销售数据...")
    success = update_sales_data()
    if success:
        logger.info("✅ 数据更新完成")
    else:
        logger.error("❌ 数据更新失败")

def update_areas():
    """更新面积数据"""
    logger.info("🚀 开始更新面积数据...")
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(__file__))
        from scrapers.area_scraper import scrape_areas_data
        scrape_areas_data()
        logger.info("✅ 面积数据更新完成")
    except Exception as e:
        logger.error(f"❌ 面积数据更新失败: {e}")

def main():
    """主函数"""
    # 配置日志 - 同时输出到控制台和文件
    # import os
    # 获取项目根目录
    # project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # log_file = os.path.join(project_root, 'logs', 'house_data.log')
    # os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()  # 控制台输出
            # logging.FileHandler(log_file, encoding='utf-8')  # 文件输出
        ]
    )
    
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "areas":
            update_areas()
        elif command == "data":
            update_data()
        else:
            logger.info("用法: PYTHONPATH=/path/to/core python3 core/main.py [areas|data]")
    else:
        # 默认更新数据
        update_data()

if __name__ == "__main__":
    main()