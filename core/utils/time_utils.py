"""
时区相关工具函数
- 提供对 zoneinfo (Python 3.9+) 的兼容支持，若没有则回退到 pytz
- 提供设置进程时区（通过 TZ 环境变量 + time.tzset）的方法
- 提供获取时区感知当前时间的方法
"""
from datetime import datetime
import os
import time

# 优先使用标准库 zoneinfo（Python >= 3.9），否则回退到 pytz
try:
    from zoneinfo import ZoneInfo
    def get_zone(tz_name: str = "Asia/Shanghai"):
        return ZoneInfo(tz_name)

    def now_in_zone(tz_name: str = "Asia/Shanghai") -> datetime:
        return datetime.now(get_zone(tz_name))
except Exception:
    try:
        import pytz
        def get_zone(tz_name: str = "Asia/Shanghai"):
            return pytz.timezone(tz_name)

        def now_in_zone(tz_name: str = "Asia/Shanghai") -> datetime:
            return datetime.now(get_zone(tz_name))
    except Exception:
        # 最后兜底：返回本地时间（naive），不建议长期使用
        def get_zone(tz_name: str = "Asia/Shanghai"):
            return None

        def now_in_zone(tz_name: str = "Asia/Shanghai") -> datetime:
            return datetime.now()


def set_process_tz(tz_name: str = "Asia/Shanghai"):
    """设置进程时区：导出 TZ 并调用 time.tzset()（在类 Unix 系统上有效）。"""
    try:
        os.environ['TZ'] = tz_name
        if hasattr(time, 'tzset'):
            time.tzset()
    except Exception:
        # 不要抛异常，保持稳健
        pass
