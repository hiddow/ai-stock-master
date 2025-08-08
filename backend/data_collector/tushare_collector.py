"""
Tushare数据采集器
"""
import tushare as ts
import pandas as pd
from typing import List, Optional
from datetime import datetime, timedelta
import logging
import time

from .base import BaseCollector
from ..config import settings

logger = logging.getLogger(__name__)

class TushareCollector(BaseCollector):
    """Tushare数据采集器"""
    
    def __init__(self, token: Optional[str] = None):
        super().__init__("tushare")
        self.token = token or settings.tushare_token
        if not self.token:
            raise ValueError("Tushare token未配置，请在.env文件中设置TUSHARE_TOKEN")
        
        # 初始化Tushare
        ts.set_token(self.token)
        self.pro = ts.pro_api()
        self.logger.info("Tushare数据采集器初始化成功")
    
    def get_stock_list(self) -> pd.DataFrame:
        """
        获取A股股票列表
        返回: DataFrame，包含股票代码、名称、上市日期等信息
        """
        try:
            # 获取股票基本信息
            df = self.pro.stock_basic(
                exchange='',  # 交易所 SSE上交所 SZSE深交所
                list_status='L',  # 上市状态 L上市 D退市 P暂停上市
                fields='ts_code,symbol,name,area,industry,list_date,market,exchange'
            )
            
            # 添加简化的股票代码（去掉后缀）
            df['code'] = df['symbol']
            
            self.logger.info(f"获取到{len(df)}只股票信息")
            return df
        except Exception as e:
            self.logger.error(f"获取股票列表失败: {e}")
            raise
    
    def get_daily_data(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取股票日K线数据
        
        参数:
            code: 股票代码（如'000001'）
            start_date: 开始日期（格式：'20210101'）
            end_date: 结束日期（格式：'20211231'）
        
        返回:
            DataFrame，包含日期、开高低收、成交量等数据
        """
        try:
            # 转换股票代码格式（添加后缀）
            ts_code = self._get_ts_code(code)
            
            # 获取日线数据
            df = self.pro.daily(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date
            )
            
            if df.empty:
                self.logger.warning(f"股票{code}在{start_date}到{end_date}期间无数据")
                return df
            
            # 按日期排序
            df = df.sort_values('trade_date')
            
            # 重命名列名为更通用的格式
            df = df.rename(columns={
                'trade_date': 'date',
                'vol': 'volume',
                'pre_close': 'prev_close',
                'pct_chg': 'change_pct'
            })
            
            self.logger.info(f"获取股票{code}日K线数据{len(df)}条")
            return df
        except Exception as e:
            self.logger.error(f"获取股票{code}日K线数据失败: {e}")
            raise
    
    def get_realtime_data(self, codes: List[str]) -> pd.DataFrame:
        """
        获取实时行情数据
        
        参数:
            codes: 股票代码列表
        
        返回:
            DataFrame，包含实时价格、涨跌幅等数据
        """
        try:
            # 转换股票代码格式
            ts_codes = [self._get_ts_code(code) for code in codes]
            ts_codes_str = ','.join(ts_codes)
            
            # 获取实时数据
            df = ts.realtime_quotes(ts_codes_str)
            
            if df is None or df.empty:
                self.logger.warning(f"未获取到实时数据")
                return pd.DataFrame()
            
            # 选择需要的列
            df = df[['code', 'name', 'price', 'bid', 'ask', 'volume', 
                    'amount', 'pre_close', 'open', 'high', 'low', 'date', 'time']]
            
            # 计算涨跌幅
            df['change_pct'] = (df['price'].astype(float) - df['pre_close'].astype(float)) / df['pre_close'].astype(float) * 100
            
            self.logger.info(f"获取{len(df)}只股票实时数据")
            return df
        except Exception as e:
            self.logger.error(f"获取实时数据失败: {e}")
            raise
    
    def get_financial_data(self, code: str, period: str = None) -> pd.DataFrame:
        """
        获取财务数据
        
        参数:
            code: 股票代码
            period: 报告期（如'20210331'）
        
        返回:
            DataFrame，包含财务指标数据
        """
        try:
            ts_code = self._get_ts_code(code)
            
            # 获取财务指标数据
            df = self.pro.fina_indicator(ts_code=ts_code, period=period)
            
            if df.empty:
                self.logger.warning(f"股票{code}无财务数据")
                return df
            
            self.logger.info(f"获取股票{code}财务数据{len(df)}条")
            return df
        except Exception as e:
            self.logger.error(f"获取股票{code}财务数据失败: {e}")
            raise
    
    def get_index_daily(self, index_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取指数日线数据
        
        参数:
            index_code: 指数代码（如'000001.SH'代表上证指数）
            start_date: 开始日期
            end_date: 结束日期
        
        返回:
            DataFrame，包含指数日线数据
        """
        try:
            df = self.pro.index_daily(
                ts_code=index_code,
                start_date=start_date,
                end_date=end_date
            )
            
            if df.empty:
                self.logger.warning(f"指数{index_code}在{start_date}到{end_date}期间无数据")
                return df
            
            # 按日期排序
            df = df.sort_values('trade_date')
            
            self.logger.info(f"获取指数{index_code}日线数据{len(df)}条")
            return df
        except Exception as e:
            self.logger.error(f"获取指数{index_code}数据失败: {e}")
            raise
    
    def get_trade_calendar(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取交易日历
        
        参数:
            start_date: 开始日期
            end_date: 结束日期
        
        返回:
            DataFrame，包含交易日信息
        """
        try:
            df = self.pro.trade_cal(
                exchange='SSE',
                start_date=start_date,
                end_date=end_date
            )
            
            # 只保留交易日
            df = df[df['is_open'] == 1]
            
            self.logger.info(f"获取交易日历，共{len(df)}个交易日")
            return df
        except Exception as e:
            self.logger.error(f"获取交易日历失败: {e}")
            raise
    
    def _get_ts_code(self, code: str) -> str:
        """
        转换股票代码为Tushare格式
        
        参数:
            code: 股票代码（如'000001'）
        
        返回:
            Tushare格式的股票代码（如'000001.SZ'）
        """
        if '.' in code:
            return code
        
        # 根据股票代码判断交易所
        if code.startswith('6'):
            return f"{code}.SH"  # 上交所
        elif code.startswith(('0', '3')):
            return f"{code}.SZ"  # 深交所
        elif code.startswith('8'):
            return f"{code}.BJ"  # 北交所
        else:
            return code