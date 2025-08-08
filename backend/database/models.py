"""
数据库模型定义
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Text, Index, Boolean
from sqlalchemy.sql import func
from datetime import datetime

from .database import Base

class Stock(Base):
    """股票基本信息表"""
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, index=True, comment="股票代码")
    name = Column(String(50), comment="股票名称")
    exchange = Column(String(10), comment="交易所")
    industry = Column(String(50), comment="所属行业")
    market = Column(String(20), comment="市场板块")
    list_date = Column(Date, comment="上市日期")
    status = Column(String(10), default="active", comment="状态")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_stock_code', 'code'),
        Index('idx_stock_industry', 'industry'),
    )

class StockDaily(Base):
    """股票日线数据表"""
    __tablename__ = "stock_daily"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), index=True, comment="股票代码")
    date = Column(Date, index=True, comment="交易日期")
    open = Column(Float, comment="开盘价")
    high = Column(Float, comment="最高价")
    low = Column(Float, comment="最低价")
    close = Column(Float, comment="收盘价")
    volume = Column(Float, comment="成交量")
    amount = Column(Float, comment="成交额")
    change_pct = Column(Float, comment="涨跌幅")
    turnover = Column(Float, comment="换手率")
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index('idx_daily_code_date', 'code', 'date'),
        Index('idx_daily_date', 'date'),
    )

class StockRealtime(Base):
    """股票实时数据表"""
    __tablename__ = "stock_realtime"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), index=True, comment="股票代码")
    name = Column(String(50), comment="股票名称")
    price = Column(Float, comment="当前价格")
    change_pct = Column(Float, comment="涨跌幅")
    volume = Column(Float, comment="成交量")
    amount = Column(Float, comment="成交额")
    open = Column(Float, comment="今开")
    high = Column(Float, comment="最高")
    low = Column(Float, comment="最低")
    pre_close = Column(Float, comment="昨收")
    timestamp = Column(DateTime, default=func.now(), comment="数据时间")
    
    __table_args__ = (
        Index('idx_realtime_code', 'code'),
        Index('idx_realtime_timestamp', 'timestamp'),
    )

class StockFinancial(Base):
    """股票财务数据表"""
    __tablename__ = "stock_financial"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), index=True, comment="股票代码")
    report_date = Column(Date, comment="报告期")
    revenue = Column(Float, comment="营业收入")
    net_profit = Column(Float, comment="净利润")
    eps = Column(Float, comment="每股收益")
    roe = Column(Float, comment="净资产收益率")
    pe = Column(Float, comment="市盈率")
    pb = Column(Float, comment="市净率")
    gross_margin = Column(Float, comment="毛利率")
    debt_ratio = Column(Float, comment="负债率")
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index('idx_financial_code_date', 'code', 'report_date'),
    )

class TechnicalIndicator(Base):
    """技术指标表"""
    __tablename__ = "technical_indicators"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), index=True, comment="股票代码")
    date = Column(Date, index=True, comment="日期")
    ma5 = Column(Float, comment="5日均线")
    ma10 = Column(Float, comment="10日均线")
    ma20 = Column(Float, comment="20日均线")
    ma60 = Column(Float, comment="60日均线")
    rsi = Column(Float, comment="RSI指标")
    macd = Column(Float, comment="MACD")
    macd_signal = Column(Float, comment="MACD信号线")
    macd_hist = Column(Float, comment="MACD柱状图")
    bb_upper = Column(Float, comment="布林带上轨")
    bb_middle = Column(Float, comment="布林带中轨")
    bb_lower = Column(Float, comment="布林带下轨")
    kdj_k = Column(Float, comment="KDJ-K值")
    kdj_d = Column(Float, comment="KDJ-D值")
    kdj_j = Column(Float, comment="KDJ-J值")
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index('idx_indicator_code_date', 'code', 'date'),
    )

class PredictionResult(Base):
    """预测结果表"""
    __tablename__ = "prediction_results"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), index=True, comment="股票代码")
    model_name = Column(String(50), comment="模型名称")
    prediction_date = Column(Date, comment="预测日期")
    prediction_type = Column(String(20), comment="预测类型")  # price, trend, signal
    prediction_value = Column(Float, comment="预测值")
    confidence = Column(Float, comment="置信度")
    actual_value = Column(Float, comment="实际值")
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index('idx_prediction_code_date', 'code', 'prediction_date'),
    )

class TradeSignal(Base):
    """交易信号表"""
    __tablename__ = "trade_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), index=True, comment="股票代码")
    signal_date = Column(Date, comment="信号日期")
    signal_type = Column(String(10), comment="信号类型")  # buy, sell, hold
    signal_strength = Column(Float, comment="信号强度")
    strategy_name = Column(String(50), comment="策略名称")
    reason = Column(Text, comment="信号原因")
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index('idx_signal_code_date', 'code', 'signal_date'),
    )

class WatchList(Base):
    """关注列表"""
    __tablename__ = "watch_list"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), default="default", comment="用户ID")
    code = Column(String(10), index=True, comment="股票代码")
    name = Column(String(50), comment="股票名称")
    add_price = Column(Float, comment="添加时价格")
    target_price = Column(Float, comment="目标价格")
    stop_loss_price = Column(Float, comment="止损价格")
    notes = Column(Text, comment="备注")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_watch_user_code', 'user_id', 'code'),
    )