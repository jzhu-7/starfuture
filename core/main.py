"""
主入口模块
统一的数据更新入口
"""
import logging
from .processors.data_processor import update_sales_data
from .utils.time_utils import set_process_tz

logger = logging.getLogger(__name__)

def update_data(project: str = None):
    """更新销售数据（可指定项目：house|warehouse）"""
    logger.info(f"🚀 开始更新销售数据... project={project}")
    success = update_sales_data(project or 'house')
    if success:
        logger.info("✅ 数据更新完成")
    else:
        logger.error("❌ 数据更新失败")


def update_areas(project: str = None):
    """更新面积数据（可指定项目）"""
    logger.info(f"🚀 开始更新面积数据... project={project}")
    try:
        from .scrapers.area_scraper import scrape_areas_data
        # area scraper may read/write files under data/{project}/areas — ensure it can accept a project if necessary
        scrape_areas_data(project=project) if 'project' in scrape_areas_data.__code__.co_varnames else scrape_areas_data()
        logger.info("✅ 面积数据更新完成")
    except Exception as e:
        logger.error(f"❌ 面积数据更新失败: {e}")


def main():
    """主函数"""
    # 设定进程默认时区（UTC/其他服务器默认时区可能不同）
    set_process_tz()

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
        project = sys.argv[2] if len(sys.argv) > 2 else None
        if command == "areas":
            update_areas(project)
        elif command == "data":
            update_data(project)
        else:
            logger.info("用法: PYTHONPATH=/path/to/core python3 core/main.py [areas|data] [project]")
    else:
        # 默认更新数据（默认项目）
        update_data()

if __name__ == "__main__":
    main()