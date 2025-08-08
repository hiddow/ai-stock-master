"""
策略回测模块
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, initial_capital: float = 100000):
        """
        初始化回测引擎
        
        参数:
            initial_capital: 初始资金
        """
        self.initial_capital = initial_capital
        self.logger = logging.getLogger(__name__)
    
    def run_backtest(self, 
                    df: pd.DataFrame, 
                    signal_column: str = 'signal_final',
                    price_column: str = 'close') -> Dict:
        """
        运行回测
        
        参数:
            df: 包含价格和信号的DataFrame
            signal_column: 信号列名
            price_column: 价格列名
        
        返回:
            回测结果字典
        """
        try:
            # 复制数据避免修改原始数据
            data = df.copy()
            
            # 初始化回测变量
            capital = self.initial_capital
            position = 0
            trades = []
            capital_history = []
            
            # 遍历每一天
            for i in range(len(data)):
                row = data.iloc[i]
                signal = row.get(signal_column, 0)
                price = row[price_column]
                date = row.get('date', i)
                
                # 买入信号
                if signal == 1 and position == 0:
                    shares = int(capital * 0.95 / price)  # 使用95%资金买入
                    if shares > 0:
                        position = shares
                        capital -= shares * price
                        trades.append({
                            'date': date,
                            'type': 'buy',
                            'price': price,
                            'shares': shares,
                            'capital': capital
                        })
                
                # 卖出信号
                elif signal == -1 and position > 0:
                    capital += position * price
                    trades.append({
                        'date': date,
                        'type': 'sell',
                        'price': price,
                        'shares': position,
                        'capital': capital
                    })
                    position = 0
                
                # 记录每日资产
                total_value = capital + position * price
                capital_history.append({
                    'date': date,
                    'capital': capital,
                    'position_value': position * price,
                    'total_value': total_value
                })
            
            # 计算最终收益
            final_value = capital + position * data.iloc[-1][price_column]
            
            # 计算统计指标
            results = self.calculate_metrics(
                trades=trades,
                capital_history=capital_history,
                initial_capital=self.initial_capital,
                final_value=final_value
            )
            
            results['trades'] = trades
            results['capital_history'] = capital_history
            
            self.logger.info(f"回测完成，总收益率: {results['total_return']:.2%}")
            return results
            
        except Exception as e:
            self.logger.error(f"回测失败: {e}")
            raise
    
    def calculate_metrics(self, 
                         trades: List[Dict],
                         capital_history: List[Dict],
                         initial_capital: float,
                         final_value: float) -> Dict:
        """
        计算回测指标
        """
        metrics = {}
        
        # 总收益率
        metrics['total_return'] = (final_value - initial_capital) / initial_capital
        
        # 交易次数
        metrics['total_trades'] = len(trades)
        metrics['buy_trades'] = len([t for t in trades if t['type'] == 'buy'])
        metrics['sell_trades'] = len([t for t in trades if t['type'] == 'sell'])
        
        # 计算胜率
        if metrics['sell_trades'] > 0:
            wins = 0
            for i in range(0, len(trades)-1, 2):
                if i+1 < len(trades):
                    buy_price = trades[i]['price']
                    sell_price = trades[i+1]['price']
                    if sell_price > buy_price:
                        wins += 1
            metrics['win_rate'] = wins / metrics['sell_trades'] if metrics['sell_trades'] > 0 else 0
        else:
            metrics['win_rate'] = 0
        
        # 计算最大回撤
        if capital_history:
            values = [h['total_value'] for h in capital_history]
            metrics['max_drawdown'] = self.calculate_max_drawdown(values)
            
            # 计算夏普比率
            returns = pd.Series(values).pct_change().dropna()
            if len(returns) > 0:
                metrics['sharpe_ratio'] = self.calculate_sharpe_ratio(returns)
            else:
                metrics['sharpe_ratio'] = 0
        else:
            metrics['max_drawdown'] = 0
            metrics['sharpe_ratio'] = 0
        
        # 最终资产
        metrics['final_value'] = final_value
        metrics['initial_capital'] = initial_capital
        
        return metrics
    
    def calculate_max_drawdown(self, values: List[float]) -> float:
        """
        计算最大回撤
        """
        if not values:
            return 0
        
        peak = values[0]
        max_dd = 0
        
        for value in values:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd
        
        return max_dd
    
    def calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.03) -> float:
        """
        计算夏普比率
        """
        if len(returns) == 0:
            return 0
        
        # 年化收益率
        annual_return = returns.mean() * 252
        
        # 年化波动率
        annual_vol = returns.std() * np.sqrt(252)
        
        if annual_vol == 0:
            return 0
        
        # 夏普比率
        sharpe = (annual_return - risk_free_rate) / annual_vol
        
        return sharpe
    
    def analyze_trades(self, trades: List[Dict]) -> Dict:
        """
        分析交易详情
        """
        if not trades:
            return {}
        
        analysis = {
            'total_trades': len(trades),
            'buy_count': 0,
            'sell_count': 0,
            'avg_buy_price': 0,
            'avg_sell_price': 0,
            'total_profit': 0,
            'profit_trades': 0,
            'loss_trades': 0
        }
        
        buy_prices = []
        sell_prices = []
        
        for trade in trades:
            if trade['type'] == 'buy':
                analysis['buy_count'] += 1
                buy_prices.append(trade['price'])
            else:
                analysis['sell_count'] += 1
                sell_prices.append(trade['price'])
        
        if buy_prices:
            analysis['avg_buy_price'] = np.mean(buy_prices)
        
        if sell_prices:
            analysis['avg_sell_price'] = np.mean(sell_prices)
        
        # 计算每对买卖的收益
        for i in range(min(len(buy_prices), len(sell_prices))):
            profit = sell_prices[i] - buy_prices[i]
            analysis['total_profit'] += profit
            if profit > 0:
                analysis['profit_trades'] += 1
            else:
                analysis['loss_trades'] += 1
        
        return analysis