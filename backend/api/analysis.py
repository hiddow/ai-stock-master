"""
分析相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import pandas as pd
from datetime import datetime
import logging

from backend.database import get_db, StockDaily, TechnicalIndicator
from backend.analysis import TechnicalAnalyzer, BacktestEngine
from backend.schemas import TechnicalIndicatorResponse, BacktestResult

router = APIRouter()

# 初始化分析器
technical_analyzer = TechnicalAnalyzer()
backtest_engine = BacktestEngine()

# 配置logger
logger = logging.getLogger(__name__)

@router.get("/{code}/technical")
async def analyze_technical(
    code: str,
    start_date: str = Query(..., description="开始日期，格式：20210101"),
    end_date: str = Query(..., description="结束日期，格式：20211231"),
    db: Session = Depends(get_db)
):
    """计算技术指标"""
    try:
        logger.info(f"开始分析股票 {code}，日期范围：{start_date} 到 {end_date}")
        
        # 解析日期
        try:
            start_dt = datetime.strptime(start_date, "%Y%m%d").date()
            end_dt = datetime.strptime(end_date, "%Y%m%d").date()
        except ValueError as e:
            # 尝试其他格式
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
                end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
            except:
                logger.error(f"日期格式错误: {e}")
                raise HTTPException(status_code=400, detail=f"日期格式错误: {e}")
        
        logger.info(f"日期解析成功：{start_dt} 到 {end_dt}")
        
        # 获取股票数据
        daily_data = db.query(StockDaily).filter(
            StockDaily.code == code,
            StockDaily.date >= start_dt,
            StockDaily.date <= end_dt
        ).order_by(StockDaily.date).all()
        
        logger.info(f"查询到 {len(daily_data)} 条数据")
        
        if not daily_data:
            logger.warning(f"没有找到股票 {code} 的数据")
            raise HTTPException(status_code=404, detail="没有找到股票数据")
        
        # 转换为DataFrame
        df = pd.DataFrame([{
            'date': d.date,
            'open': float(d.open) if d.open else 0,
            'high': float(d.high) if d.high else 0,
            'low': float(d.low) if d.low else 0,
            'close': float(d.close) if d.close else 0,
            'volume': float(d.volume) if d.volume else 0
        } for d in daily_data])
        
        logger.info(f"DataFrame创建成功，shape: {df.shape}")
        
        # 计算技术指标
        df_with_indicators = technical_analyzer.calculate_all_indicators(df)
        logger.info("技术指标计算成功")
        
        # 生成交易信号
        df_with_signals = technical_analyzer.generate_signals(df_with_indicators)
        logger.info("交易信号生成成功")
        
        # 存储技术指标到数据库
        for _, row in df_with_indicators.iterrows():
            indicator = TechnicalIndicator(
                code=code,
                date=row['date'],
                ma5=row.get('ma5'),
                ma10=row.get('ma10'),
                ma20=row.get('ma20'),
                ma60=row.get('ma60'),
                rsi=row.get('rsi'),
                macd=row.get('macd'),
                macd_signal=row.get('macd_signal'),
                macd_hist=row.get('macd_hist'),
                bb_upper=row.get('bb_upper'),
                bb_middle=row.get('bb_middle'),
                bb_lower=row.get('bb_lower'),
                kdj_k=row.get('kdj_k'),
                kdj_d=row.get('kdj_d'),
                kdj_j=row.get('kdj_j')
            )
            db.merge(indicator)  # 使用merge避免重复
        db.commit()
        
        # 转换numpy类型为Python原生类型
        indicators_list = []
        for record in df_with_indicators.to_dict('records'):
            cleaned_record = {}
            for key, value in record.items():
                if pd.isna(value):
                    cleaned_record[key] = None
                elif hasattr(value, 'item'):  # numpy类型
                    cleaned_record[key] = value.item()
                else:
                    cleaned_record[key] = value
            indicators_list.append(cleaned_record)
        
        # 获取最后的信号
        latest_signal = 0
        signal_strength = 0
        if not df_with_signals.empty:
            last_row = df_with_signals.iloc[-1]
            latest_signal = int(last_row.get('signal_final', 0)) if not pd.isna(last_row.get('signal_final', 0)) else 0
            signal_strength = float(last_row.get('signal_strength', 0)) if not pd.isna(last_row.get('signal_strength', 0)) else 0
        
        # 返回结果
        return {
            "code": code,
            "period": f"{start_date} - {end_date}",
            "indicators": indicators_list,
            "latest_signal": latest_signal,
            "signal_strength": signal_strength
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"分析股票 {code} 失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{code}/backtest")
async def run_backtest(
    code: str,
    start_date: str = Query(..., description="开始日期，格式：20210101"),
    end_date: str = Query(..., description="结束日期，格式：20211231"),
    initial_capital: float = Query(100000, description="初始资金"),
    db: Session = Depends(get_db)
):
    """运行回测"""
    try:
        # 获取股票数据
        daily_data = db.query(StockDaily).filter(
            StockDaily.code == code,
            StockDaily.date >= datetime.strptime(start_date, "%Y%m%d").date(),
            StockDaily.date <= datetime.strptime(end_date, "%Y%m%d").date()
        ).order_by(StockDaily.date).all()
        
        if not daily_data:
            raise HTTPException(status_code=404, detail="没有找到股票数据")
        
        # 转换为DataFrame
        df = pd.DataFrame([{
            'date': d.date,
            'open': d.open,
            'high': d.high,
            'low': d.low,
            'close': d.close,
            'volume': d.volume
        } for d in daily_data])
        
        # 计算技术指标和信号
        df_with_indicators = technical_analyzer.calculate_all_indicators(df)
        df_with_signals = technical_analyzer.generate_signals(df_with_indicators)
        
        # 运行回测
        backtest_engine.initial_capital = initial_capital
        results = backtest_engine.run_backtest(df_with_signals)
        
        return {
            "code": code,
            "period": f"{start_date} - {end_date}",
            "metrics": {
                "total_return": results['total_return'],
                "win_rate": results['win_rate'],
                "max_drawdown": results['max_drawdown'],
                "sharpe_ratio": results['sharpe_ratio'],
                "total_trades": results['total_trades'],
                "final_value": results['final_value']
            },
            "trades": results.get('trades', [])[:20],  # 返回最近20笔交易
            "summary": f"总收益率: {results['total_return']:.2%}, 胜率: {results['win_rate']:.2%}, 最大回撤: {results['max_drawdown']:.2%}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{code}/signals")
async def get_trade_signals(
    code: str,
    days: int = Query(30, description="最近天数"),
    db: Session = Depends(get_db)
):
    """获取交易信号"""
    try:
        # 获取最近的股票数据
        daily_data = db.query(StockDaily).filter(
            StockDaily.code == code
        ).order_by(StockDaily.date.desc()).limit(days + 60).all()  # 多获取一些数据用于计算指标
        
        if not daily_data:
            raise HTTPException(status_code=404, detail="没有找到股票数据")
        
        # 转换为DataFrame并反转（因为是倒序查询的）
        df = pd.DataFrame([{
            'date': d.date,
            'open': d.open,
            'high': d.high,
            'low': d.low,
            'close': d.close,
            'volume': d.volume
        } for d in reversed(daily_data)])
        
        # 计算技术指标和信号
        df_with_indicators = technical_analyzer.calculate_all_indicators(df)
        df_with_signals = technical_analyzer.generate_signals(df_with_indicators)
        
        # 只返回最近的信号
        recent_signals = df_with_signals.tail(days)
        
        # 筛选出有信号的日期
        signals = []
        for _, row in recent_signals.iterrows():
            if row.get('signal_final', 0) != 0:
                signals.append({
                    'date': row['date'].strftime('%Y-%m-%d') if hasattr(row['date'], 'strftime') else str(row['date']),
                    'signal': 'buy' if row['signal_final'] > 0 else 'sell',
                    'strength': row.get('signal_strength', 0),
                    'price': row['close'],
                    'indicators': {
                        'rsi': row.get('rsi'),
                        'macd': row.get('macd'),
                        'ma5': row.get('ma5'),
                        'ma20': row.get('ma20')
                    }
                })
        
        return {
            "code": code,
            "total_signals": len(signals),
            "signals": signals,
            "latest_signal": signals[-1] if signals else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))