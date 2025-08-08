"""
Gemini AI 分析 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import pandas as pd
import logging
from datetime import datetime, timedelta
from PIL import Image
import io

from backend.database import get_db, StockDaily, TechnicalIndicator, Stock
from backend.ai_models import GeminiAnalyzer, GeminiFastAnalyzer

router = APIRouter()
logger = logging.getLogger(__name__)

# 初始化 Gemini 分析器
gemini_analyzer = GeminiAnalyzer()
gemini_fast = GeminiFastAnalyzer()


@router.post("/{code}/comprehensive")
async def gemini_comprehensive_analysis(
    code: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    使用 Gemini 进行股票综合分析
    """
    try:
        # 获取股票基本信息
        stock = db.query(Stock).filter(Stock.code == code).first()
        if not stock:
            raise HTTPException(status_code=404, detail=f"股票 {code} 不存在")
        
        # 获取历史数据
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        daily_data = db.query(StockDaily).filter(
            StockDaily.code == code,
            StockDaily.date >= start_date,
            StockDaily.date <= end_date
        ).order_by(StockDaily.date).all()
        
        if not daily_data:
            raise HTTPException(status_code=404, detail=f"股票 {code} 没有历史数据")
        
        # 转换为 DataFrame
        df = pd.DataFrame([{
            'date': d.date,
            'open': float(d.open) if d.open else 0,
            'high': float(d.high) if d.high else 0,
            'low': float(d.low) if d.low else 0,
            'close': float(d.close) if d.close else 0,
            'volume': float(d.volume) if d.volume else 0,
            'change_pct': float(d.change_pct) if d.change_pct else 0
        } for d in daily_data])
        
        # 获取最新技术指标
        latest_indicator = db.query(TechnicalIndicator).filter(
            TechnicalIndicator.code == code
        ).order_by(TechnicalIndicator.date.desc()).first()
        
        technical_data = None
        if latest_indicator:
            technical_data = {
                'rsi': float(latest_indicator.rsi) if latest_indicator.rsi else None,
                'macd': float(latest_indicator.macd) if latest_indicator.macd else None,
                'ma5': float(latest_indicator.ma5) if latest_indicator.ma5 else None,
                'ma20': float(latest_indicator.ma20) if latest_indicator.ma20 else None,
                'kdj_k': float(latest_indicator.kdj_k) if latest_indicator.kdj_k else None
            }
        
        # 调用 Gemini 分析
        result = gemini_analyzer.analyze_stock_comprehensive(
            code=code,
            stock_data=df,
            technical_indicators=technical_data,
            financial_data=None  # 暂无财务数据
        )
        
        return {
            "status": "success",
            "stock": {
                "code": stock.code,
                "name": stock.name
            },
            "gemini_analysis": result,
            "data_points": len(daily_data),
            "period": f"{start_date} 至 {end_date}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Gemini 综合分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chart-analysis")
async def analyze_chart(
    file: UploadFile = File(...)
):
    """
    分析上传的K线图
    """
    try:
        # 读取图片
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # 调用 Gemini 分析
        result = gemini_analyzer.analyze_chart_pattern(image)
        
        return {
            "status": "success",
            "filename": file.filename,
            "analysis": result
        }
        
    except Exception as e:
        logger.error(f"图表分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{code}/quick-signal")
async def get_quick_signal(
    code: str,
    db: Session = Depends(get_db)
):
    """
    获取快速交易信号
    """
    try:
        # 获取最新数据
        latest = db.query(StockDaily).filter(
            StockDaily.code == code
        ).order_by(StockDaily.date.desc()).first()
        
        if not latest:
            raise HTTPException(status_code=404, detail=f"股票 {code} 没有数据")
        
        # 获取最新技术指标
        indicator = db.query(TechnicalIndicator).filter(
            TechnicalIndicator.code == code,
            TechnicalIndicator.date == latest.date
        ).first()
        
        latest_data = {
            'price': float(latest.close) if latest.close else 0,
            'change_pct': float(latest.change_pct) if latest.change_pct else 0,
            'volume_ratio': 1.0,  # 需要计算
            'rsi': float(indicator.rsi) if indicator and indicator.rsi else 50,
            'macd': float(indicator.macd) if indicator and indicator.macd else 0
        }
        
        # 获取快速信号
        signal = gemini_analyzer.quick_signal(code, latest_data)
        
        return signal
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取快速信号失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-analyze")
async def batch_analyze_stocks(
    codes: List[str],
    db: Session = Depends(get_db)
):
    """
    批量分析股票
    """
    try:
        stock_list = []
        
        for code in codes[:10]:  # 限制数量
            latest = db.query(StockDaily).filter(
                StockDaily.code == code
            ).order_by(StockDaily.date.desc()).first()
            
            if latest:
                stock_list.append({
                    'code': code,
                    'price': float(latest.close) if latest.close else 0,
                    'change_pct': float(latest.change_pct) if latest.change_pct else 0,
                    'volume': float(latest.volume) if latest.volume else 0
                })
        
        # 批量分析
        results = gemini_analyzer.batch_analyze(stock_list)
        
        return {
            "status": "success",
            "analyzed_count": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"批量分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitor/alerts")
async def get_monitoring_alerts(
    db: Session = Depends(get_db)
):
    """
    获取实时监控警报
    """
    try:
        # 获取最新的股票数据
        latest_date = db.query(StockDaily.date).order_by(
            StockDaily.date.desc()
        ).first()
        
        if not latest_date:
            return {"alerts": []}
        
        # 获取当日所有股票数据
        daily_stocks = db.query(StockDaily).filter(
            StockDaily.date == latest_date[0]
        ).all()
        
        stock_list = []
        for stock in daily_stocks:
            stock_list.append({
                'code': stock.code,
                'name': stock.code,  # 需要关联 Stock 表获取名称
                'price': float(stock.close) if stock.close else 0,
                'change_pct': float(stock.change_pct) if stock.change_pct else 0,
                'volume': float(stock.volume) if stock.volume else 0,
                'volume_ratio': 1.0  # 需要计算
            })
        
        # 监控异动
        alerts = gemini_fast.monitor_realtime(stock_list)
        
        return {
            "status": "success",
            "alerts": alerts,
            "monitored_stocks": len(stock_list),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取监控警报失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask")
async def ask_gemini(
    question: str,
    context: Optional[Dict] = None
):
    """
    向 Gemini 提问
    """
    try:
        if not gemini_analyzer.client:
            raise HTTPException(status_code=503, detail="Gemini 服务不可用")
        
        # 构建上下文
        prompt = question
        if context:
            prompt = f"""
            上下文信息：
            {context}
            
            问题：{question}
            """
        
        # 调用 Gemini
        response = gemini_analyzer.client.models.generate_content(
            model=gemini_analyzer.fast_model,
            contents=prompt,
            config={
                "temperature": 0.7,
                "max_output_tokens": 500
            }
        )
        
        return {
            "status": "success",
            "question": question,
            "answer": response.text,
            "model": gemini_analyzer.fast_model,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Gemini 问答失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))