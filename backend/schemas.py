"""
Pydantic数据模型定义
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import date, datetime

class StockInfo(BaseModel):
    """股票基本信息"""
    code: str
    name: str
    exchange: Optional[str] = None
    industry: Optional[str] = None
    market: Optional[str] = None
    list_date: Optional[date] = None
    status: str = "active"
    
    class Config:
        from_attributes = True

class StockDailyBase(BaseModel):
    """股票日线数据基础模型"""
    code: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: Optional[float] = None
    change_pct: Optional[float] = None
    turnover: Optional[float] = None

class StockDaily(StockDailyBase):
    """股票日线数据"""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class StockRealtimeBase(BaseModel):
    """股票实时数据基础模型"""
    code: str
    name: str
    price: float
    change_pct: float
    volume: float
    amount: float
    open: float
    high: float
    low: float
    pre_close: float

class StockRealtime(StockRealtimeBase):
    """股票实时数据"""
    id: Optional[int] = None
    timestamp: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class TechnicalIndicatorResponse(BaseModel):
    """技术指标响应"""
    code: str
    period: str
    indicators: List[Dict[str, Any]]
    latest_signal: int
    signal_strength: float

class BacktestResult(BaseModel):
    """回测结果"""
    code: str
    period: str
    metrics: Dict[str, float]
    trades: List[Dict[str, Any]]
    summary: str

class TradeSignalResponse(BaseModel):
    """交易信号响应"""
    code: str
    signal_date: date
    signal_type: str  # buy, sell, hold
    signal_strength: float
    strategy_name: str
    reason: Optional[str] = None
    
    class Config:
        from_attributes = True

class PredictionResponse(BaseModel):
    """预测结果响应"""
    code: str
    model_name: str
    prediction_date: date
    prediction_type: str
    prediction_value: float
    confidence: float
    
    class Config:
        from_attributes = True

class WatchListCreate(BaseModel):
    """创建关注列表项"""
    code: str
    target_price: Optional[float] = None
    stop_loss_price: Optional[float] = None
    notes: Optional[str] = None
    add_price: Optional[float] = None

class WatchListUpdate(BaseModel):
    """更新关注列表项"""
    target_price: Optional[float] = None
    stop_loss_price: Optional[float] = None
    notes: Optional[str] = None

class WatchListItem(BaseModel):
    """关注列表项"""
    id: int
    code: str
    name: str
    add_price: float
    current_price: float
    change_pct: float
    target_price: Optional[float] = None
    stop_loss_price: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True