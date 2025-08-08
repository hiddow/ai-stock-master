"""
AI预测模型框架（简化版）
使用基础的统计方法和简单的机器学习模型
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging
import json
import os

logger = logging.getLogger(__name__)

class SimplePricePredictor:
    """简单价格预测器 - 基于移动平均和趋势分析"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model_params = {}
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """准备特征数据"""
        df = df.copy()
        
        # 计算价格变化率
        df['price_change'] = df['close'].pct_change()
        
        # 计算移动平均
        for period in [5, 10, 20]:
            df[f'ma{period}'] = df['close'].rolling(window=period).mean()
            df[f'ma{period}_ratio'] = df['close'] / df[f'ma{period}']
        
        # 计算波动率
        df['volatility'] = df['price_change'].rolling(window=20).std()
        
        # 成交量特征
        df['volume_ma'] = df['volume'].rolling(window=10).mean()
        df['volume_ratio'] = df['volume'] / df['volume_ma']
        
        # 价格位置（相对于最高最低价）
        df['price_position'] = (df['close'] - df['low']) / (df['high'] - df['low'])
        
        return df
    
    def predict_next_day(self, df: pd.DataFrame) -> Dict:
        """预测下一个交易日的价格"""
        # 准备特征
        df_features = self.prepare_features(df)
        
        # 获取最近的数据
        if len(df_features) < 20:
            return {
                'prediction': None,
                'confidence': 0,
                'reason': '数据不足'
            }
        
        latest = df_features.iloc[-1]
        
        # 简单的趋势预测
        # 1. 短期趋势（5日）
        short_trend = (latest['close'] - df_features.iloc[-5]['close']) / df_features.iloc[-5]['close']
        
        # 2. 中期趋势（20日）
        mid_trend = (latest['close'] - df_features.iloc[-20]['close']) / df_features.iloc[-20]['close']
        
        # 3. 均线位置
        ma_score = 0
        if latest['ma5_ratio'] > 1:
            ma_score += 0.3
        if latest['ma10_ratio'] > 1:
            ma_score += 0.3
        if latest['ma20_ratio'] > 1:
            ma_score += 0.4
        
        # 4. 成交量信号
        volume_signal = 1 if latest['volume_ratio'] > 1.2 else 0
        
        # 综合预测
        trend_score = short_trend * 0.5 + mid_trend * 0.3 + ma_score * 0.2
        
        # 预测价格变化率
        predicted_change = trend_score * 0.02  # 限制在2%以内
        
        # 预测价格
        predicted_price = latest['close'] * (1 + predicted_change)
        
        # 计算置信度
        confidence = min(abs(trend_score) * 100, 80)  # 最高80%置信度
        
        # 生成预测理由
        reasons = []
        if short_trend > 0.01:
            reasons.append("短期上升趋势")
        elif short_trend < -0.01:
            reasons.append("短期下降趋势")
        
        if ma_score > 0.5:
            reasons.append("价格位于均线上方")
        elif ma_score < 0.3:
            reasons.append("价格位于均线下方")
        
        if volume_signal:
            reasons.append("成交量放大")
        
        return {
            'prediction': predicted_price,
            'current_price': latest['close'],
            'predicted_change': predicted_change,
            'confidence': confidence,
            'trend': 'up' if predicted_change > 0 else 'down',
            'reasons': reasons
        }
    
    def predict_trend(self, df: pd.DataFrame, days: int = 5) -> Dict:
        """预测未来几天的趋势"""
        df_features = self.prepare_features(df)
        
        if len(df_features) < 30:
            return {
                'trend': 'unknown',
                'confidence': 0,
                'predictions': []
            }
        
        predictions = []
        current_df = df_features.copy()
        
        for i in range(days):
            pred = self.predict_next_day(current_df)
            if pred['prediction']:
                predictions.append({
                    'day': i + 1,
                    'price': pred['prediction'],
                    'change': pred['predicted_change']
                })
                
                # 添加预测值作为新的一行（简化处理）
                new_row = current_df.iloc[-1].copy()
                new_row['close'] = pred['prediction']
                current_df = pd.concat([current_df, new_row.to_frame().T], ignore_index=True)
        
        # 判断总体趋势
        if predictions:
            total_change = (predictions[-1]['price'] - df_features.iloc[-1]['close']) / df_features.iloc[-1]['close']
            if total_change > 0.02:
                trend = 'bullish'
            elif total_change < -0.02:
                trend = 'bearish'
            else:
                trend = 'neutral'
        else:
            trend = 'unknown'
        
        return {
            'trend': trend,
            'days': days,
            'predictions': predictions,
            'confidence': 60  # 简单模型，置信度设为60%
        }

class PatternRecognizer:
    """K线形态识别器"""
    
    def __init__(self):
        self.patterns = {
            'hammer': self.detect_hammer,
            'doji': self.detect_doji,
            'engulfing': self.detect_engulfing,
            'morning_star': self.detect_morning_star,
            'evening_star': self.detect_evening_star
        }
    
    def detect_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """检测所有K线形态"""
        patterns_found = []
        
        for pattern_name, detect_func in self.patterns.items():
            result = detect_func(df)
            if result:
                patterns_found.extend(result)
        
        return patterns_found
    
    def detect_hammer(self, df: pd.DataFrame) -> List[Dict]:
        """检测锤子线"""
        patterns = []
        
        for i in range(1, len(df)):
            row = df.iloc[i]
            body = abs(row['close'] - row['open'])
            lower_shadow = min(row['open'], row['close']) - row['low']
            upper_shadow = row['high'] - max(row['open'], row['close'])
            
            # 锤子线条件：下影线是实体的2倍以上，上影线很小
            if lower_shadow > body * 2 and upper_shadow < body * 0.5:
                patterns.append({
                    'date': row.get('date', i),
                    'pattern': 'hammer',
                    'signal': 'bullish',
                    'description': '锤子线，可能见底信号'
                })
        
        return patterns
    
    def detect_doji(self, df: pd.DataFrame) -> List[Dict]:
        """检测十字星"""
        patterns = []
        
        for i in range(len(df)):
            row = df.iloc[i]
            body = abs(row['close'] - row['open'])
            total_range = row['high'] - row['low']
            
            # 十字星条件：实体很小
            if total_range > 0 and body / total_range < 0.1:
                patterns.append({
                    'date': row.get('date', i),
                    'pattern': 'doji',
                    'signal': 'neutral',
                    'description': '十字星，趋势可能反转'
                })
        
        return patterns
    
    def detect_engulfing(self, df: pd.DataFrame) -> List[Dict]:
        """检测吞没形态"""
        patterns = []
        
        for i in range(1, len(df)):
            curr = df.iloc[i]
            prev = df.iloc[i-1]
            
            # 看涨吞没
            if (prev['close'] < prev['open'] and  # 前一天是阴线
                curr['close'] > curr['open'] and  # 当天是阳线
                curr['open'] < prev['close'] and  # 开盘价低于前一天收盘
                curr['close'] > prev['open']):    # 收盘价高于前一天开盘
                
                patterns.append({
                    'date': curr.get('date', i),
                    'pattern': 'bullish_engulfing',
                    'signal': 'bullish',
                    'description': '看涨吞没，强烈买入信号'
                })
            
            # 看跌吞没
            elif (prev['close'] > prev['open'] and  # 前一天是阳线
                  curr['close'] < curr['open'] and  # 当天是阴线
                  curr['open'] > prev['close'] and  # 开盘价高于前一天收盘
                  curr['close'] < prev['open']):    # 收盘价低于前一天开盘
                
                patterns.append({
                    'date': curr.get('date', i),
                    'pattern': 'bearish_engulfing',
                    'signal': 'bearish',
                    'description': '看跌吞没，强烈卖出信号'
                })
        
        return patterns
    
    def detect_morning_star(self, df: pd.DataFrame) -> List[Dict]:
        """检测早晨之星"""
        patterns = []
        
        for i in range(2, len(df)):
            first = df.iloc[i-2]
            second = df.iloc[i-1]
            third = df.iloc[i]
            
            # 早晨之星条件
            if (first['close'] < first['open'] and  # 第一天是长阴线
                abs(second['close'] - second['open']) < abs(first['close'] - first['open']) * 0.3 and  # 第二天是小实体
                third['close'] > third['open'] and  # 第三天是阳线
                third['close'] > (first['open'] + first['close']) / 2):  # 第三天收盘高于第一天中点
                
                patterns.append({
                    'date': third.get('date', i),
                    'pattern': 'morning_star',
                    'signal': 'bullish',
                    'description': '早晨之星，底部反转信号'
                })
        
        return patterns
    
    def detect_evening_star(self, df: pd.DataFrame) -> List[Dict]:
        """检测黄昏之星"""
        patterns = []
        
        for i in range(2, len(df)):
            first = df.iloc[i-2]
            second = df.iloc[i-1]
            third = df.iloc[i]
            
            # 黄昏之星条件
            if (first['close'] > first['open'] and  # 第一天是长阳线
                abs(second['close'] - second['open']) < abs(first['close'] - first['open']) * 0.3 and  # 第二天是小实体
                third['close'] < third['open'] and  # 第三天是阴线
                third['close'] < (first['open'] + first['close']) / 2):  # 第三天收盘低于第一天中点
                
                patterns.append({
                    'date': third.get('date', i),
                    'pattern': 'evening_star',
                    'signal': 'bearish',
                    'description': '黄昏之星，顶部反转信号'
                })
        
        return patterns