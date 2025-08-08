"""
技术指标计算模块
"""
import pandas as pd
import numpy as np
import ta
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    """技术指标分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算所有技术指标
        
        参数:
            df: 包含OHLCV数据的DataFrame（必须包含open, high, low, close, volume列）
        
        返回:
            包含所有技术指标的DataFrame
        """
        try:
            # 确保数据按日期排序
            if 'date' in df.columns:
                df = df.sort_values('date')
            
            # 计算移动平均线
            df = self.calculate_ma(df)
            
            # 计算RSI
            df = self.calculate_rsi(df)
            
            # 计算MACD
            df = self.calculate_macd(df)
            
            # 计算布林带
            df = self.calculate_bollinger_bands(df)
            
            # 计算KDJ
            df = self.calculate_kdj(df)
            
            # 计算成交量指标
            df = self.calculate_volume_indicators(df)
            
            self.logger.info(f"计算技术指标完成，共{len(df)}条数据")
            return df
        except Exception as e:
            self.logger.error(f"计算技术指标失败: {e}")
            raise
    
    def calculate_ma(self, df: pd.DataFrame, periods: list = [5, 10, 20, 60]) -> pd.DataFrame:
        """
        计算移动平均线
        """
        for period in periods:
            df[f'ma{period}'] = df['close'].rolling(window=period).mean()
        return df
    
    def calculate_ema(self, df: pd.DataFrame, periods: list = [12, 26]) -> pd.DataFrame:
        """
        计算指数移动平均线
        """
        for period in periods:
            df[f'ema{period}'] = df['close'].ewm(span=period, adjust=False).mean()
        return df
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        计算RSI相对强弱指标
        """
        df['rsi'] = ta.momentum.RSIIndicator(close=df['close'], window=period).rsi()
        return df
    
    def calculate_macd(self, df: pd.DataFrame, 
                      fast_period: int = 12, 
                      slow_period: int = 26, 
                      signal_period: int = 9) -> pd.DataFrame:
        """
        计算MACD指标
        """
        macd_indicator = ta.trend.MACD(
            close=df['close'],
            window_slow=slow_period,
            window_fast=fast_period,
            window_sign=signal_period
        )
        
        df['macd'] = macd_indicator.macd()
        df['macd_signal'] = macd_indicator.macd_signal()
        df['macd_hist'] = macd_indicator.macd_diff()
        
        return df
    
    def calculate_bollinger_bands(self, df: pd.DataFrame, 
                                 period: int = 20, 
                                 std_dev: int = 2) -> pd.DataFrame:
        """
        计算布林带
        """
        bb_indicator = ta.volatility.BollingerBands(
            close=df['close'],
            window=period,
            window_dev=std_dev
        )
        
        df['bb_upper'] = bb_indicator.bollinger_hband()
        df['bb_middle'] = bb_indicator.bollinger_mavg()
        df['bb_lower'] = bb_indicator.bollinger_lband()
        df['bb_width'] = bb_indicator.bollinger_wband()
        df['bb_percent'] = bb_indicator.bollinger_pband()
        
        return df
    
    def calculate_kdj(self, df: pd.DataFrame, 
                     n: int = 9, 
                     m1: int = 3, 
                     m2: int = 3) -> pd.DataFrame:
        """
        计算KDJ指标
        """
        # 计算RSV
        low_n = df['low'].rolling(window=n, min_periods=1).min()
        high_n = df['high'].rolling(window=n, min_periods=1).max()
        rsv = (df['close'] - low_n) / (high_n - low_n) * 100
        
        # 计算K值
        df['kdj_k'] = rsv.ewm(com=m1-1, adjust=False).mean()
        
        # 计算D值
        df['kdj_d'] = df['kdj_k'].ewm(com=m2-1, adjust=False).mean()
        
        # 计算J值
        df['kdj_j'] = 3 * df['kdj_k'] - 2 * df['kdj_d']
        
        return df
    
    def calculate_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算成交量相关指标
        """
        # 成交量移动平均
        df['volume_ma5'] = df['volume'].rolling(window=5).mean()
        df['volume_ma10'] = df['volume'].rolling(window=10).mean()
        
        # 成交量比率
        df['volume_ratio'] = df['volume'] / df['volume_ma5']
        
        # OBV（On Balance Volume）
        df['obv'] = ta.volume.OnBalanceVolumeIndicator(
            close=df['close'],
            volume=df['volume']
        ).on_balance_volume()
        
        return df
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        计算ATR（Average True Range）平均真实波幅
        """
        df['atr'] = ta.volatility.AverageTrueRange(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            window=period
        ).average_true_range()
        
        return df
    
    def calculate_cci(self, df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """
        计算CCI（Commodity Channel Index）商品通道指数
        """
        df['cci'] = ta.trend.CCIIndicator(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            window=period
        ).cci()
        
        return df
    
    def calculate_williams_r(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        计算威廉指标
        """
        df['williams_r'] = ta.momentum.WilliamsRIndicator(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            lbp=period
        ).williams_r()
        
        return df
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        根据技术指标生成交易信号
        """
        # 初始化信号列
        df['signal'] = 0
        df['signal_strength'] = 0
        
        signals = []
        
        # MA金叉死叉信号
        if 'ma5' in df.columns and 'ma20' in df.columns:
            df['ma_signal'] = np.where(
                (df['ma5'] > df['ma20']) & (df['ma5'].shift(1) <= df['ma20'].shift(1)), 1,
                np.where(
                    (df['ma5'] < df['ma20']) & (df['ma5'].shift(1) >= df['ma20'].shift(1)), -1, 0
                )
            )
            signals.append('ma_signal')
        
        # RSI超买超卖信号
        if 'rsi' in df.columns:
            df['rsi_signal'] = np.where(
                df['rsi'] < 30, 1,  # 超卖，买入信号
                np.where(df['rsi'] > 70, -1, 0)  # 超买，卖出信号
            )
            signals.append('rsi_signal')
        
        # MACD金叉死叉信号
        if 'macd' in df.columns and 'macd_signal' in df.columns:
            df['macd_cross_signal'] = np.where(
                (df['macd'] > df['macd_signal']) & (df['macd'].shift(1) <= df['macd_signal'].shift(1)), 1,
                np.where(
                    (df['macd'] < df['macd_signal']) & (df['macd'].shift(1) >= df['macd_signal'].shift(1)), -1, 0
                )
            )
            signals.append('macd_cross_signal')
        
        # 布林带信号
        if 'bb_upper' in df.columns and 'bb_lower' in df.columns:
            df['bb_signal'] = np.where(
                df['close'] < df['bb_lower'], 1,  # 触及下轨，买入信号
                np.where(df['close'] > df['bb_upper'], -1, 0)  # 触及上轨，卖出信号
            )
            signals.append('bb_signal')
        
        # KDJ信号
        if 'kdj_k' in df.columns and 'kdj_d' in df.columns:
            df['kdj_signal'] = np.where(
                (df['kdj_k'] > df['kdj_d']) & (df['kdj_k'].shift(1) <= df['kdj_d'].shift(1)) & (df['kdj_k'] < 20), 1,
                np.where(
                    (df['kdj_k'] < df['kdj_d']) & (df['kdj_k'].shift(1) >= df['kdj_d'].shift(1)) & (df['kdj_k'] > 80), -1, 0
                )
            )
            signals.append('kdj_signal')
        
        # 综合信号
        if signals:
            df['signal'] = df[signals].sum(axis=1)
            df['signal_strength'] = abs(df['signal']) / len(signals)
            
            # 将信号标准化为-1, 0, 1
            df['signal_final'] = np.where(
                df['signal'] > 0, 1,
                np.where(df['signal'] < 0, -1, 0)
            )
        
        return df