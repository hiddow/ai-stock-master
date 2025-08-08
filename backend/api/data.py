"""
数据管理API路由
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import logging

from backend.database import get_db, Stock, StockDaily
from backend.data_collector import AkShareCollector, TushareCollector
from backend.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/update/stock-list")
async def update_stock_list(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """更新股票列表"""
    try:
        collector = AkShareCollector()
        df = collector.get_stock_list()
        
        updated = 0
        added = 0
        
        for _, row in df.iterrows():
            existing = db.query(Stock).filter(Stock.code == row['code']).first()
            if existing:
                existing.name = row['name']
                updated += 1
            else:
                stock = Stock(
                    code=row['code'],
                    name=row['name']
                )
                db.add(stock)
                added += 1
        
        db.commit()
        
        return {
            "message": "股票列表更新成功",
            "added": added,
            "updated": updated,
            "total": len(df)
        }
    except Exception as e:
        logger.error(f"更新股票列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update/daily/{code}")
async def update_stock_daily(
    code: str,
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db)
):
    """更新指定股票的日线数据"""
    try:
        collector = AkShareCollector()
        df = collector.get_daily_data(code, start_date, end_date)
        
        if df.empty:
            return {"message": "没有新数据"}
        
        added = 0
        for _, row in df.iterrows():
            from datetime import datetime
            
            date_obj = datetime.strptime(str(row['date']), "%Y%m%d").date()
            
            # 检查是否已存在
            existing = db.query(StockDaily).filter(
                StockDaily.code == code,
                StockDaily.date == date_obj
            ).first()
            
            if not existing:
                daily = StockDaily(
                    code=code,
                    date=date_obj,
                    open=row['open'],
                    high=row['high'],
                    low=row['low'],
                    close=row['close'],
                    volume=row['volume'],
                    amount=row.get('amount', 0),
                    change_pct=row.get('change_pct', 0),
                    turnover=row.get('turnover', 0)
                )
                db.add(daily)
                added += 1
        
        db.commit()
        
        return {
            "message": f"股票{code}日线数据更新成功",
            "added": added,
            "period": f"{start_date} - {end_date}"
        }
    except Exception as e:
        logger.error(f"更新股票{code}日线数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_data_status(db: Session = Depends(get_db)):
    """获取数据状态"""
    try:
        stock_count = db.query(Stock).count()
        daily_count = db.query(StockDaily).count()
        
        # 获取最新的数据日期
        latest_daily = db.query(StockDaily).order_by(StockDaily.date.desc()).first()
        
        return {
            "stock_count": stock_count,
            "daily_records": daily_count,
            "latest_date": latest_daily.date if latest_daily else None,
            "database_url": settings.database_url,
            "data_source": "AkShare"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/clear/{table_name}")
async def clear_table_data(
    table_name: str,
    db: Session = Depends(get_db)
):
    """清空指定表的数据（谨慎使用）"""
    try:
        allowed_tables = {
            "stock_daily": StockDaily,
            "stock_realtime": "stock_realtime",
            "technical_indicators": "technical_indicators",
            "prediction_results": "prediction_results",
            "trade_signals": "trade_signals"
        }
        
        if table_name not in allowed_tables:
            raise HTTPException(status_code=400, detail="不允许清空该表")
        
        if isinstance(allowed_tables[table_name], str):
            # 直接执行SQL
            db.execute(f"DELETE FROM {allowed_tables[table_name]}")
        else:
            # 使用ORM
            db.query(allowed_tables[table_name]).delete()
        
        db.commit()
        
        return {"message": f"表{table_name}已清空"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))