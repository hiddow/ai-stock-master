"""
关注列表API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from backend.database import get_db, WatchList, Stock, StockDaily, StockRealtime
from backend.schemas import WatchListItem, WatchListCreate, WatchListUpdate
from backend.ai_models import SimplePricePredictor, PatternRecognizer
from backend.analysis import TechnicalAnalyzer
import pandas as pd

router = APIRouter()
logger = logging.getLogger(__name__)

# 初始化分析器
predictor = SimplePricePredictor()
pattern_recognizer = PatternRecognizer()
technical_analyzer = TechnicalAnalyzer()

@router.get("/list", response_model=List[WatchListItem])
async def get_watch_list(
    user_id: str = Query("default", description="用户ID"),
    db: Session = Depends(get_db)
):
    """获取关注列表"""
    watch_list = db.query(WatchList).filter(
        WatchList.user_id == user_id,
        WatchList.is_active == True
    ).order_by(WatchList.created_at.desc()).all()
    
    # 获取每只股票的最新价格和涨跌幅
    result = []
    for item in watch_list:
        # 获取最新价格
        realtime = db.query(StockRealtime).filter(
            StockRealtime.code == item.code
        ).order_by(StockRealtime.timestamp.desc()).first()
        
        # 获取最近的日K数据
        daily = db.query(StockDaily).filter(
            StockDaily.code == item.code
        ).order_by(StockDaily.date.desc()).first()
        
        current_price = realtime.price if realtime else (daily.close if daily else item.add_price)
        change_pct = ((current_price - item.add_price) / item.add_price * 100) if item.add_price else 0
        
        result.append({
            "id": item.id,
            "code": item.code,
            "name": item.name,
            "add_price": item.add_price,
            "current_price": current_price,
            "change_pct": change_pct,
            "target_price": item.target_price,
            "stop_loss_price": item.stop_loss_price,
            "notes": item.notes,
            "created_at": item.created_at
        })
    
    return result

@router.post("/add")
async def add_to_watch_list(
    watch_item: WatchListCreate,
    user_id: str = Query("default"),
    db: Session = Depends(get_db)
):
    """添加到关注列表"""
    # 检查是否已存在
    existing = db.query(WatchList).filter(
        WatchList.user_id == user_id,
        WatchList.code == watch_item.code,
        WatchList.is_active == True
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="该股票已在关注列表中")
    
    # 获取股票信息
    stock = db.query(Stock).filter(Stock.code == watch_item.code).first()
    if not stock:
        raise HTTPException(status_code=404, detail="股票不存在")
    
    # 获取当前价格
    realtime = db.query(StockRealtime).filter(
        StockRealtime.code == watch_item.code
    ).order_by(StockRealtime.timestamp.desc()).first()
    
    current_price = realtime.price if realtime else watch_item.add_price
    
    # 创建关注记录
    watch_list_item = WatchList(
        user_id=user_id,
        code=watch_item.code,
        name=stock.name,
        add_price=current_price or 0,
        target_price=watch_item.target_price,
        stop_loss_price=watch_item.stop_loss_price,
        notes=watch_item.notes
    )
    
    db.add(watch_list_item)
    db.commit()
    db.refresh(watch_list_item)
    
    return {"message": "添加成功", "id": watch_list_item.id}

@router.delete("/{watch_id}")
async def remove_from_watch_list(
    watch_id: int,
    db: Session = Depends(get_db)
):
    """从关注列表移除"""
    watch_item = db.query(WatchList).filter(WatchList.id == watch_id).first()
    
    if not watch_item:
        raise HTTPException(status_code=404, detail="关注记录不存在")
    
    watch_item.is_active = False
    db.commit()
    
    return {"message": "移除成功"}

@router.put("/{watch_id}")
async def update_watch_item(
    watch_id: int,
    update_data: WatchListUpdate,
    db: Session = Depends(get_db)
):
    """更新关注项"""
    watch_item = db.query(WatchList).filter(WatchList.id == watch_id).first()
    
    if not watch_item:
        raise HTTPException(status_code=404, detail="关注记录不存在")
    
    if update_data.target_price is not None:
        watch_item.target_price = update_data.target_price
    if update_data.stop_loss_price is not None:
        watch_item.stop_loss_price = update_data.stop_loss_price
    if update_data.notes is not None:
        watch_item.notes = update_data.notes
    
    db.commit()
    
    return {"message": "更新成功"}

@router.get("/{code}/analysis")
async def get_watch_stock_analysis(
    code: str,
    db: Session = Depends(get_db)
):
    """获取关注股票的详细分析和预测"""
    # 获取股票基本信息
    stock = db.query(Stock).filter(Stock.code == code).first()
    if not stock:
        raise HTTPException(status_code=404, detail="股票不存在")
    
    # 获取最近60天的K线数据
    daily_data = db.query(StockDaily).filter(
        StockDaily.code == code
    ).order_by(StockDaily.date.desc()).limit(60).all()
    
    if not daily_data:
        raise HTTPException(status_code=404, detail="没有历史数据")
    
    # 转换为DataFrame
    df = pd.DataFrame([{
        'date': d.date,
        'open': d.open,
        'high': d.high,
        'low': d.low,
        'close': d.close,
        'volume': d.volume
    } for d in reversed(daily_data)])
    
    # 技术分析
    df_with_indicators = technical_analyzer.calculate_all_indicators(df)
    df_with_signals = technical_analyzer.generate_signals(df_with_indicators)
    
    # AI预测
    prediction = predictor.predict_next_day(df)
    trend_prediction = predictor.predict_trend(df, days=5)
    
    # K线形态识别
    patterns = pattern_recognizer.detect_patterns(df)
    
    # 生成详细的分析报告
    latest = df_with_indicators.iloc[-1]
    
    analysis_report = {
        "stock_info": {
            "code": code,
            "name": stock.name,
            "industry": stock.industry
        },
        "current_status": {
            "price": latest['close'],
            "ma5": latest.get('ma5'),
            "ma20": latest.get('ma20'),
            "rsi": latest.get('rsi'),
            "macd": latest.get('macd'),
            "volume_ratio": latest.get('volume_ratio')
        },
        "technical_signals": {
            "signal": int(df_with_signals.iloc[-1].get('signal_final', 0)),
            "strength": float(df_with_signals.iloc[-1].get('signal_strength', 0)),
            "ma_trend": "上升" if latest.get('ma5', 0) > latest.get('ma20', 0) else "下降",
            "volume_trend": "放量" if latest.get('volume_ratio', 1) > 1.2 else "缩量"
        },
        "ai_prediction": {
            "next_day": {
                "price": prediction['prediction'],
                "change": prediction['predicted_change'],
                "confidence": prediction['confidence'],
                "reasons": prediction.get('reasons', [])
            },
            "five_day_trend": trend_prediction
        },
        "patterns": patterns[-5:] if patterns else [],
        "detailed_analysis": generate_detailed_analysis(
            stock, latest, prediction, patterns, df_with_signals
        ),
        "risk_assessment": generate_risk_assessment(
            latest, prediction, df_with_indicators
        ),
        "investment_suggestion": generate_investment_suggestion(
            latest, prediction, df_with_signals, patterns
        )
    }
    
    return analysis_report

def generate_detailed_analysis(stock, latest, prediction, patterns, signals_df):
    """生成详细分析说明"""
    analysis = []
    
    # 1. 趋势分析
    ma_analysis = ""
    if latest.get('ma5', 0) > latest.get('ma20', 0):
        ma_analysis = "股价位于短期均线上方，短期趋势向好。"
        if latest.get('ma5', 0) > latest.get('ma60', 0):
            ma_analysis += "同时突破中长期均线，中期趋势转强。"
    else:
        ma_analysis = "股价位于短期均线下方，短期承压。"
        if latest.get('ma20', 0) < latest.get('ma60', 0):
            ma_analysis += "中期均线也呈下降趋势，需谨慎观察。"
    analysis.append({"type": "趋势分析", "content": ma_analysis})
    
    # 2. 技术指标分析
    rsi_analysis = ""
    rsi_value = latest.get('rsi', 50)
    if rsi_value > 70:
        rsi_analysis = f"RSI指标为{rsi_value:.1f}，处于超买区域，短期可能有回调压力。"
    elif rsi_value < 30:
        rsi_analysis = f"RSI指标为{rsi_value:.1f}，处于超卖区域，可能存在反弹机会。"
    else:
        rsi_analysis = f"RSI指标为{rsi_value:.1f}，处于中性区域，暂无明显超买超卖信号。"
    analysis.append({"type": "动量分析", "content": rsi_analysis})
    
    # 3. MACD分析
    macd_analysis = ""
    if latest.get('macd', 0) > 0:
        if latest.get('macd_hist', 0) > 0:
            macd_analysis = "MACD在零轴上方且柱状图为正，多头趋势明显。"
        else:
            macd_analysis = "MACD在零轴上方但柱状图转负，上涨动能减弱。"
    else:
        if latest.get('macd_hist', 0) > 0:
            macd_analysis = "MACD在零轴下方但柱状图转正，可能出现反转信号。"
        else:
            macd_analysis = "MACD在零轴下方且柱状图为负，空头趋势持续。"
    analysis.append({"type": "MACD分析", "content": macd_analysis})
    
    # 4. 成交量分析
    volume_analysis = ""
    volume_ratio = latest.get('volume_ratio', 1)
    if volume_ratio > 1.5:
        volume_analysis = f"成交量放大{volume_ratio:.1f}倍，"
        if prediction['predicted_change'] > 0:
            volume_analysis += "配合上涨趋势，资金流入明显。"
        else:
            volume_analysis += "但价格下跌，需警惕主力出货。"
    elif volume_ratio < 0.7:
        volume_analysis = "成交量萎缩，市场交投清淡，观望情绪浓厚。"
    else:
        volume_analysis = "成交量保持正常水平，无明显异动。"
    analysis.append({"type": "量能分析", "content": volume_analysis})
    
    # 5. K线形态分析
    if patterns:
        recent_pattern = patterns[-1]
        pattern_analysis = f"近期出现{recent_pattern['pattern']}形态，"
        if recent_pattern['signal'] == 'bullish':
            pattern_analysis += "这是看涨信号，可能预示价格上涨。"
        elif recent_pattern['signal'] == 'bearish':
            pattern_analysis += "这是看跌信号，需要注意风险。"
        else:
            pattern_analysis += "市场处于震荡整理阶段。"
        analysis.append({"type": "形态分析", "content": pattern_analysis})
    
    # 6. 支撑压力分析
    support = latest['close'] * 0.95
    resistance = latest['close'] * 1.05
    support_resistance = f"技术支撑位在{support:.2f}附近，压力位在{resistance:.2f}附近。"
    if latest.get('bb_lower'):
        support_resistance += f"布林带下轨{latest['bb_lower']:.2f}提供动态支撑。"
    analysis.append({"type": "支撑压力", "content": support_resistance})
    
    return analysis

def generate_risk_assessment(latest, prediction, df_indicators):
    """生成风险评估"""
    risk_score = 50  # 基础风险分
    risk_factors = []
    
    # RSI风险
    rsi = latest.get('rsi', 50)
    if rsi > 80:
        risk_score += 20
        risk_factors.append("RSI严重超买，回调风险高")
    elif rsi > 70:
        risk_score += 10
        risk_factors.append("RSI超买，有一定回调风险")
    elif rsi < 20:
        risk_score -= 10
        risk_factors.append("RSI严重超卖，下跌风险降低")
    
    # 波动率风险
    volatility = df_indicators['close'].pct_change().std() * 100
    if volatility > 5:
        risk_score += 15
        risk_factors.append(f"波动率较高({volatility:.1f}%)，价格波动剧烈")
    elif volatility < 2:
        risk_score -= 5
        risk_factors.append("波动率较低，价格相对稳定")
    
    # 趋势风险
    if latest.get('ma5', 0) < latest.get('ma20', 0):
        risk_score += 10
        risk_factors.append("短期均线在长期均线下方，趋势偏弱")
    
    # 成交量风险
    if latest.get('volume_ratio', 1) < 0.5:
        risk_score += 5
        risk_factors.append("成交量严重萎缩，流动性风险")
    
    # 限制风险分数范围
    risk_score = max(0, min(100, risk_score))
    
    risk_level = "低" if risk_score < 30 else "中" if risk_score < 70 else "高"
    
    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "suggestion": get_risk_suggestion(risk_level)
    }

def generate_investment_suggestion(latest, prediction, signals_df, patterns):
    """生成投资建议"""
    signal = signals_df.iloc[-1].get('signal_final', 0)
    confidence = prediction.get('confidence', 50)
    
    # 综合评分
    score = 50
    if signal > 0:
        score += 20
    elif signal < 0:
        score -= 20
    
    if prediction['predicted_change'] > 0:
        score += confidence / 5
    else:
        score -= confidence / 5
    
    if patterns and patterns[-1]['signal'] == 'bullish':
        score += 10
    elif patterns and patterns[-1]['signal'] == 'bearish':
        score -= 10
    
    # 生成建议
    if score > 70:
        action = "买入"
        position = "建议仓位30-50%"
        reason = "技术指标和AI预测均显示积极信号"
    elif score > 50:
        action = "观望"
        position = "建议小仓位试探，不超过20%"
        reason = "信号不够明确，建议等待更好机会"
    else:
        action = "卖出/回避"
        position = "建议清仓或回避"
        reason = "技术指标显示负面信号，风险较大"
    
    return {
        "score": score,
        "action": action,
        "position": position,
        "reason": reason,
        "entry_points": [
            latest['close'] * 0.98,
            latest['close'] * 0.96
        ],
        "exit_points": [
            latest['close'] * 1.03,
            latest['close'] * 1.06
        ],
        "stop_loss": latest['close'] * 0.93
    }

def get_risk_suggestion(risk_level):
    """根据风险等级生成建议"""
    suggestions = {
        "低": "风险较低，可以正常操作，但仍需设置止损。",
        "中": "风险适中，建议控制仓位，分批建仓，严格止损。",
        "高": "风险较高，不建议追高，等待回调或观望为主。"
    }
    return suggestions.get(risk_level, "请谨慎评估风险")