"""
Gemini AI 分析模块
使用 Gemini 2.0 Flash 进行股票分析
"""
import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd
import numpy as np
from PIL import Image
import io
import base64

from google import genai
from google.genai import types

from backend.config import settings

logger = logging.getLogger(__name__)


class GeminiAnalyzer:
    """Gemini 主分析器 - 用于深度股票分析"""
    
    def __init__(self):
        """初始化 Gemini 客户端"""
        self.api_key = settings.gemini_api_key
        if not self.api_key:
            logger.warning("GEMINI_API_KEY 未设置，Gemini 功能将不可用")
            self.client = None
        else:
            try:
                self.client = genai.Client(api_key=self.api_key)
                self.main_model = settings.gemini_model_main
                self.fast_model = settings.gemini_model_fast
                logger.info(f"Gemini 分析器初始化成功，主模型: {self.main_model}")
            except Exception as e:
                logger.error(f"初始化 Gemini 客户端失败: {e}")
                self.client = None
    
    def analyze_stock_comprehensive(self, code: str, stock_data: pd.DataFrame, 
                                   technical_indicators: Dict = None,
                                   financial_data: Dict = None) -> Dict:
        """
        综合分析股票
        
        参数:
            code: 股票代码
            stock_data: 股票历史数据
            technical_indicators: 技术指标
            financial_data: 财务数据
        """
        if not self.client:
            return {"error": "Gemini 客户端未初始化"}
        
        try:
            # 准备分析数据
            latest_price = stock_data.iloc[-1]['close'] if not stock_data.empty else 0
            price_change = ((stock_data.iloc[-1]['close'] - stock_data.iloc[-5]['close']) 
                          / stock_data.iloc[-5]['close'] * 100) if len(stock_data) > 5 else 0
            
            # 构建提示词
            prompt = f"""
            作为专业的证券分析师，请对股票 {code} 进行综合分析：
            
            ## 基础数据
            - 当前价格：{latest_price:.2f}
            - 5日涨跌幅：{price_change:.2f}%
            - 最高价（20日）：{stock_data['high'].max():.2f}
            - 最低价（20日）：{stock_data['low'].max():.2f}
            - 平均成交量：{stock_data['volume'].mean():.0f}
            
            ## 技术指标
            {self._format_technical_indicators(technical_indicators)}
            
            ## 财务数据
            {self._format_financial_data(financial_data) if financial_data else "暂无财务数据"}
            
            请提供：
            1. 技术面分析（趋势、支撑位、阻力位）
            2. 基本面分析（如有财务数据）
            3. 短期预测（1-5天）
            4. 中期预测（1-4周）
            5. 投资建议（买入/持有/卖出）
            6. 风险提示
            7. 关键价位（止损位、目标位）
            
            请用JSON格式返回分析结果。
            """
            
            # 调用 Gemini API
            response = self.client.models.generate_content(
                model=self.main_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    response_mime_type="application/json"
                )
            )
            
            # 解析响应
            try:
                result = json.loads(response.text) if response.text else {"analysis": "无响应"}
            except (json.JSONDecodeError, AttributeError):
                result = {"raw_analysis": response.text if response.text else "解析失败"}
            
            return {
                "status": "success",
                "model": self.main_model,
                "analysis": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Gemini 综合分析失败: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def analyze_chart_pattern(self, chart_image: Any) -> Dict:
        """
        分析K线图形态
        
        参数:
            chart_image: K线图图像（PIL Image 或 bytes）
        """
        if not self.client:
            return {"error": "Gemini 客户端未初始化"}
        
        try:
            prompt = """
            请分析这个K线图，识别以下内容：
            
            1. 主要趋势（上升/下降/横盘）
            2. 重要的K线形态（如头肩顶、双底、三角形等）
            3. 支撑位和阻力位
            4. 成交量特征
            5. MACD、RSI等指标信号（如果图中包含）
            6. 买卖点建议
            
            请用JSON格式返回分析结果，包括：
            - trend: 趋势
            - patterns: 形态列表
            - support_levels: 支撑位
            - resistance_levels: 阻力位
            - signals: 交易信号
            - recommendation: 操作建议
            """
            
            # 如果是 bytes，转换为 PIL Image
            if isinstance(chart_image, bytes):
                chart_image = Image.open(io.BytesIO(chart_image))
            
            response = self.client.models.generate_content(
                model=self.fast_model,
                contents=[chart_image, prompt],
                config=types.GenerateContentConfig(
                    temperature=0.5,
                    response_mime_type="application/json"
                )
            )
            
            try:
                result = json.loads(response.text) if response.text else {"data": "无响应"}
            except (json.JSONDecodeError, AttributeError):
                result = {"raw_analysis": response.text if response.text else "解析失败"}
            
            return {
                "status": "success",
                "model": self.fast_model,
                "chart_analysis": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"K线图分析失败: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def analyze_news_sentiment(self, news_list: List[Dict]) -> Dict:
        """
        分析新闻情绪
        
        参数:
            news_list: 新闻列表，每项包含 title, content, time
        """
        if not self.client:
            return {"error": "Gemini 客户端未初始化"}
        
        try:
            news_text = "\n".join([
                f"【{news.get('time', '')}】{news.get('title', '')}: {news.get('content', '')[:200]}"
                for news in news_list[:10]  # 只分析最新10条
            ])
            
            prompt = f"""
            请分析以下股票相关新闻的市场情绪：
            
            {news_text}
            
            请提供：
            1. 整体情绪评分（-100到+100，负数看跌，正数看涨）
            2. 主要利好因素
            3. 主要利空因素
            4. 市场影响预测
            5. 建议的应对策略
            
            用JSON格式返回。
            """
            
            response = self.client.models.generate_content(
                model=self.fast_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.5,
                    response_mime_type="application/json"
                )
            )
            
            try:
                result = json.loads(response.text) if response.text else {"data": "无响应"}
            except (json.JSONDecodeError, AttributeError):
                result = {"raw_analysis": response.text if response.text else "解析失败"}
            
            return {
                "status": "success",
                "sentiment_analysis": result,
                "news_count": len(news_list),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"新闻情绪分析失败: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def quick_signal(self, code: str, latest_data: Dict) -> Dict:
        """
        快速生成交易信号
        
        参数:
            code: 股票代码
            latest_data: 最新数据（价格、成交量、技术指标等）
        """
        if not self.client:
            return {"error": "Gemini 客户端未初始化"}
        
        try:
            prompt = f"""
            基于以下数据快速判断股票 {code} 的交易信号：
            
            价格: {latest_data.get('price', 0)}
            涨跌幅: {latest_data.get('change_pct', 0)}%
            成交量比: {latest_data.get('volume_ratio', 1)}
            RSI: {latest_data.get('rsi', 50)}
            MACD: {latest_data.get('macd', 0)}
            
            请直接返回JSON格式：
            - signal: BUY/HOLD/SELL
            - strength: 1-10的信号强度
            - reason: 简短理由（50字内）
            """
            
            response = self.client.models.generate_content(
                model=self.fast_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    response_mime_type="application/json",
                    max_output_tokens=200
                )
            )
            
            try:
                result = json.loads(response.text) if response.text else {"signal": "HOLD", "strength": 5, "reason": "无响应"}
            except (json.JSONDecodeError, AttributeError):
                result = {"signal": "HOLD", "strength": 5, "reason": "解析失败"}
            
            return {
                "status": "success",
                "code": code,
                **result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"快速信号生成失败: {e}")
            return {
                "status": "error",
                "signal": "HOLD",
                "error": str(e)
            }
    
    def batch_analyze(self, stock_list: List[Dict]) -> List[Dict]:
        """
        批量分析股票
        
        参数:
            stock_list: 股票列表，每项包含 code, price, change_pct 等
        """
        if not self.client:
            return [{"error": "Gemini 客户端未初始化"}]
        
        results = []
        for stock in stock_list[:20]:  # 限制批量分析数量
            result = self.quick_signal(
                stock['code'],
                {
                    'price': stock.get('price', 0),
                    'change_pct': stock.get('change_pct', 0),
                    'volume_ratio': stock.get('volume_ratio', 1),
                    'rsi': stock.get('rsi', 50)
                }
            )
            results.append(result)
        
        return results
    
    def _format_technical_indicators(self, indicators: Dict) -> str:
        """格式化技术指标"""
        if not indicators:
            return "暂无技术指标"
        
        formatted = []
        if 'rsi' in indicators:
            formatted.append(f"RSI: {indicators['rsi']:.2f}")
        if 'macd' in indicators:
            formatted.append(f"MACD: {indicators['macd']:.3f}")
        if 'ma5' in indicators:
            formatted.append(f"MA5: {indicators['ma5']:.2f}")
        if 'ma20' in indicators:
            formatted.append(f"MA20: {indicators['ma20']:.2f}")
        
        return "\n".join(formatted) if formatted else "暂无技术指标"
    
    def _format_financial_data(self, financial: Dict) -> str:
        """格式化财务数据"""
        if not financial:
            return "暂无财务数据"
        
        formatted = []
        if 'revenue' in financial:
            formatted.append(f"营收: {financial['revenue']:.2f}亿")
        if 'net_profit' in financial:
            formatted.append(f"净利润: {financial['net_profit']:.2f}亿")
        if 'roe' in financial:
            formatted.append(f"ROE: {financial['roe']:.2f}%")
        if 'pe' in financial:
            formatted.append(f"市盈率: {financial['pe']:.2f}")
        
        return "\n".join(formatted) if formatted else "暂无财务数据"


class GeminiFastAnalyzer:
    """Gemini 快速分析器 - 用于实时监控和批量处理"""
    
    def __init__(self):
        """初始化快速分析器"""
        self.analyzer = GeminiAnalyzer()
    
    def monitor_realtime(self, stock_list: List[Dict]) -> List[Dict]:
        """
        实时监控股票
        
        参数:
            stock_list: 实时股票数据列表
        """
        if not self.analyzer.client:
            return []
        
        alerts = []
        for stock in stock_list:
            # 检查异动
            if abs(stock.get('change_pct', 0)) > 5:  # 涨跌超过5%
                signal = self.analyzer.quick_signal(stock['code'], stock)
                if signal.get('status') == 'success':
                    alerts.append({
                        'code': stock['code'],
                        'name': stock.get('name', ''),
                        'alert_type': 'PRICE_CHANGE',
                        'change_pct': stock['change_pct'],
                        'signal': signal.get('signal'),
                        'reason': signal.get('reason')
                    })
            
            # 检查成交量异常
            if stock.get('volume_ratio', 1) > 2:  # 成交量是平均的2倍以上
                alerts.append({
                    'code': stock['code'],
                    'name': stock.get('name', ''),
                    'alert_type': 'VOLUME_SPIKE',
                    'volume_ratio': stock['volume_ratio']
                })
        
        return alerts
    
    def screen_stocks(self, criteria: Dict) -> List[Dict]:
        """
        根据条件筛选股票
        
        参数:
            criteria: 筛选条件
        """
        # 这里可以调用 Gemini 进行智能筛选
        # 简化实现，实际应该连接数据库
        return []