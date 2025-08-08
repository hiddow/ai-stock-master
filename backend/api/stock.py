"""
股票相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
import pandas as pd

from backend.database import get_db, Stock, StockDaily, StockRealtime
from backend.data_collector import AkShareCollector
from backend.schemas import StockInfo, StockDaily as StockDailySchema, StockRealtime as StockRealtimeSchema

router = APIRouter()

# 初始化数据采集器
collector = AkShareCollector()

@router.get("/list", response_model=List[StockInfo])
async def get_stock_list(
    industry: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取股票列表"""
    try:
        query = db.query(Stock)
        if industry:
            query = query.filter(Stock.industry == industry)
        
        stocks = query.all()
        
        # 如果数据库为空，从数据源获取
        if not stocks:
            df = collector.get_stock_list()
            # 存入数据库
            for _, row in df.iterrows():
                stock = Stock(
                    code=row['code'],
                    name=row['name']
                )
                db.add(stock)
            db.commit()
            stocks = db.query(Stock).all()
        
        return stocks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{code}/daily", response_model=List[StockDailySchema])
async def get_stock_daily(
    code: str,
    start_date: str = Query(..., description="开始日期，格式：20210101"),
    end_date: str = Query(..., description="结束日期，格式：20211231"),
    db: Session = Depends(get_db)
):
    """获取股票日K线数据"""
    try:
        # 先从数据库查询
        daily_data = db.query(StockDaily).filter(
            StockDaily.code == code,
            StockDaily.date >= datetime.strptime(start_date, "%Y%m%d").date(),
            StockDaily.date <= datetime.strptime(end_date, "%Y%m%d").date()
        ).order_by(StockDaily.date).all()
        
        # 如果数据库没有，从数据源获取
        if not daily_data:
            df = collector.get_daily_data(code, start_date, end_date)
            
            # 存入数据库
            for _, row in df.iterrows():
                daily = StockDaily(
                    code=code,
                    date=datetime.strptime(str(row['date']), "%Y%m%d").date(),
                    open=row['open'],
                    high=row['high'],
                    low=row['low'],
                    close=row['close'],
                    volume=row['volume'],
                    amount=row.get('amount', 0),
                    change_pct=row.get('change_pct', 0)
                )
                db.add(daily)
            db.commit()
            
            daily_data = db.query(StockDaily).filter(
                StockDaily.code == code,
                StockDaily.date >= datetime.strptime(start_date, "%Y%m%d").date(),
                StockDaily.date <= datetime.strptime(end_date, "%Y%m%d").date()
            ).order_by(StockDaily.date).all()
        
        return daily_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{code}/realtime", response_model=StockRealtimeSchema)
async def get_stock_realtime(
    code: str,
    db: Session = Depends(get_db)
):
    """获取股票实时数据"""
    try:
        # 获取实时数据
        df = collector.get_realtime_data([code])
        
        if df.empty:
            raise HTTPException(status_code=404, detail="未找到股票数据")
        
        row = df.iloc[0]
        
        # 存入数据库
        realtime = StockRealtime(
            code=code,
            name=row.get('name', ''),
            price=row['price'],
            change_pct=row.get('change_pct', 0),
            volume=row.get('volume', 0),
            amount=row.get('amount', 0),
            open=row.get('open', 0),
            high=row.get('high', 0),
            low=row.get('low', 0),
            pre_close=row.get('pre_close', 0)
        )
        db.add(realtime)
        db.commit()
        
        return realtime
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{code}/info")
async def get_stock_info(
    code: str,
    db: Session = Depends(get_db)
):
    """获取股票详细信息"""
    try:
        stock = db.query(Stock).filter(Stock.code == code).first()
        
        if not stock:
            raise HTTPException(status_code=404, detail="股票不存在")
        
        # 获取最新价格
        realtime = db.query(StockRealtime).filter(
            StockRealtime.code == code
        ).order_by(StockRealtime.timestamp.desc()).first()
        
        # 获取最近的日K线数据
        daily = db.query(StockDaily).filter(
            StockDaily.code == code
        ).order_by(StockDaily.date.desc()).limit(30).all()
        
        return {
            "basic_info": stock,
            "realtime": realtime,
            "recent_daily": daily
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))