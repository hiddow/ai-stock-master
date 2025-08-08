"""
AkShare数据采集器
"""
import akshare as ak
import pandas as pd
from typing import List, Optional
from datetime import datetime
import logging

from .base import BaseCollector

logger = logging.getLogger(__name__)

class AkShareCollector(BaseCollector):
    """AkShare数据采集器 - 免费数据源，无需token"""
    
    def __init__(self):
        super().__init__("akshare")
        self.logger.info("AkShare数据采集器初始化成功")
    
    def get_stock_list(self) -> pd.DataFrame:
        """
        获取A股股票列表
        """
        try:
            # 获取A股股票列表
            df = ak.stock_info_a_code_name()
            
            # 统一列名
            df = df.rename(columns={
                'code': 'code',
                'name': 'name'
            })
            
            self.logger.info(f"获取到{len(df)}只股票信息")
            return df
        except Exception as e:
            self.logger.error(f"获取股票列表失败: {e}")
            raise
    
    def get_daily_data(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取股票日K线数据
        
        参数:
            code: 股票代码
            start_date: 开始日期（格式：'20210101'）
            end_date: 结束日期（格式：'20211231'）
        """
        try:
            # 转换日期格式为 YYYY-MM-DD
            start = datetime.strptime(start_date, "%Y%m%d").strftime("%Y%m%d")
            end = datetime.strptime(end_date, "%Y%m%d").strftime("%Y%m%d")
            
            # 获取历史数据
            df = ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=start,
                end_date=end,
                adjust="qfq"  # 前复权
            )
            
            if df.empty:
                self.logger.warning(f"股票{code}在{start_date}到{end_date}期间无数据")
                return df
            
            # 重命名列名
            df = df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount',
                '涨跌幅': 'change_pct',
                '涨跌额': 'change',
                '换手率': 'turnover'
            })
            
            # 将日期转换为字符串格式
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y%m%d')
            
            self.logger.info(f"获取股票{code}日K线数据{len(df)}条")
            return df
        except Exception as e:
            self.logger.error(f"获取股票{code}日K线数据失败: {e}")
            raise
    
    def get_realtime_data(self, codes: List[str]) -> pd.DataFrame:
        """
        获取实时行情数据
        """
        try:
            # 获取所有A股实时数据
            df = ak.stock_zh_a_spot_em()
            
            # 筛选指定股票
            if codes:
                df = df[df['代码'].isin(codes)]
            
            # 重命名列名
            df = df.rename(columns={
                '代码': 'code',
                '名称': 'name',
                '最新价': 'price',
                '涨跌幅': 'change_pct',
                '涨跌额': 'change',
                '成交量': 'volume',
                '成交额': 'amount',
                '今开': 'open',
                '最高': 'high',
                '最低': 'low',
                '昨收': 'pre_close',
                '换手率': 'turnover'
            })
            
            # 选择需要的列
            columns = ['code', 'name', 'price', 'change_pct', 'change', 
                      'volume', 'amount', 'open', 'high', 'low', 'pre_close']
            df = df[columns]
            
            self.logger.info(f"获取{len(df)}只股票实时数据")
            return df
        except Exception as e:
            self.logger.error(f"获取实时数据失败: {e}")
            raise
    
    def get_index_daily(self, index_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取指数日线数据
        
        参数:
            index_code: 指数代码（如'sh000001'代表上证指数）
            start_date: 开始日期
            end_date: 结束日期
        """
        try:
            # 获取指数历史数据
            df = ak.stock_zh_index_daily(
                symbol=index_code
            )
            
            # 转换日期格式并筛选日期范围
            df['date'] = pd.to_datetime(df['date'])
            start_dt = datetime.strptime(start_date, "%Y%m%d")
            end_dt = datetime.strptime(end_date, "%Y%m%d")
            df = df[(df['date'] >= start_dt) & (df['date'] <= end_dt)]
            
            # 转换日期为字符串格式
            df['date'] = df['date'].dt.strftime('%Y%m%d')
            
            self.logger.info(f"获取指数{index_code}日线数据{len(df)}条")
            return df
        except Exception as e:
            self.logger.error(f"获取指数{index_code}数据失败: {e}")
            raise
    
    def get_stock_fund_flow(self, code: str) -> pd.DataFrame:
        """
        获取个股资金流向
        
        参数:
            code: 股票代码
        """
        try:
            # 获取个股资金流向
            df = ak.stock_individual_fund_flow(
                stock=code,
                market="sh" if code.startswith('6') else "sz"
            )
            
            self.logger.info(f"获取股票{code}资金流向数据{len(df)}条")
            return df
        except Exception as e:
            self.logger.error(f"获取股票{code}资金流向失败: {e}")
            raise
    
    def get_stock_news(self, code: str = None) -> pd.DataFrame:
        """
        获取股票新闻
        
        参数:
            code: 股票代码（可选）
        """
        try:
            # 获取股票新闻
            df = ak.stock_news_em(symbol=code) if code else ak.stock_news_em()
            
            self.logger.info(f"获取新闻数据{len(df)}条")
            return df
        except Exception as e:
            self.logger.error(f"获取新闻数据失败: {e}")
            raise