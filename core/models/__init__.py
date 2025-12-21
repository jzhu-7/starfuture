"""
数据模型定义
"""
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class HouseData:
    """房屋数据模型"""
    house_no: str
    area: float = 0.0
    status: str = ""

@dataclass
class BuildingData:
    """楼栋数据模型"""
    building_name: str
    house_data: List[HouseData]
    status_count: Dict[str, int] = None

@dataclass
class StatusChange:
    """状态变化模型"""
    building_name: str
    house_no: str
    prev_status: str
    curr_status: str

@dataclass
class SalesStats:
    """销售统计模型"""
    signed_units: int
    signed_area: float
    avg_price: float