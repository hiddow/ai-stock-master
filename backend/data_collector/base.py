"""
基础数据采集器
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class BaseCollector(ABC):
    """数据采集器基类"""
    
    def __init__(self, source_name: str):
        self.source_name = source_name
        self.logger = logging.getLogger(f"{__name__}.{source_name}")
    
    @abstractmethod
    def get_stock_list(self) -> pd.DataFrame:
        """获取股票列表"""
        pass
    
    @abstractmethod
    def get_daily_data(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取日K线数据"""
        pass
    
    @abstractmethod
    def get_realtime_data(self, codes: List[str]) -> pd.DataFrame:
        """获取实时行情数据"""
        pass
    
    def validate_date(self, date_str: str) -> bool:
        """验证日期格式"""
        try:
            datetime.strptime(date_str, "%Y%m%d")
            return True
        except ValueError:
            return False
    
    def get_trade_dates(self, start_date: str, end_date: str) -> List[str]:
        """获取交易日列表"""
        # 这里简化处理，实际应该从交易日历获取
        start = datetime.strptime(start_date, "%Y%m%d")
        end = datetime.strptime(end_date, "%Y%m%d")
        dates = []
        current = start
        while current <= end:
            if current.weekday() < 5:  # 排除周末
                dates.append(current.strftime("%Y%m%d"))
            current += timedelta(days=1)
        return dates