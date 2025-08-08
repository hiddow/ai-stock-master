"""
AI炒股大师使用示例
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.data_collector import AkShareCollector
from backend.analysis import TechnicalAnalyzer, BacktestEngine
import pandas as pd
from datetime import datetime, timedelta

def example_data_collection():
    """数据采集示例"""
    print("\n=== 数据采集示例 ===")
    
    # 创建数据采集器
    collector = AkShareCollector()
    
    # 获取股票列表
    print("获取A股股票列表...")
    stocks = collector.get_stock_list()
    print(f"共获取到 {len(stocks)} 只股票")
    print(stocks.head())
    
    # 获取单只股票的日线数据
    code = "000001"  # 平安银行
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
    
    print(f"\n获取{code}的日线数据...")
    daily_data = collector.get_daily_data(code, start_date, end_date)
    print(daily_data.head())
    
    return daily_data

def example_technical_analysis(df):
    """技术分析示例"""
    print("\n=== 技术分析示例 ===")
    
    # 创建技术分析器
    analyzer = TechnicalAnalyzer()
    
    # 计算技术指标
    print("计算技术指标...")
    df_with_indicators = analyzer.calculate_all_indicators(df)
    
    # 显示部分指标
    print("\n最新的技术指标:")
    latest = df_with_indicators.iloc[-1]
    print(f"MA5: {latest.get('ma5', 'N/A'):.2f}")
    print(f"MA20: {latest.get('ma20', 'N/A'):.2f}")
    print(f"RSI: {latest.get('rsi', 'N/A'):.2f}")
    print(f"MACD: {latest.get('macd', 'N/A'):.4f}")
    
    # 生成交易信号
    print("\n生成交易信号...")
    df_with_signals = analyzer.generate_signals(df_with_indicators)
    
    # 显示最近的信号
    recent_signals = df_with_signals[df_with_signals['signal_final'] != 0].tail(5)
    if not recent_signals.empty:
        print("最近的交易信号:")
        for _, row in recent_signals.iterrows():
            signal_type = "买入" if row['signal_final'] > 0 else "卖出"
            print(f"  {row['date']}: {signal_type} (强度: {row['signal_strength']:.2f})")
    else:
        print("近期没有明确的交易信号")
    
    return df_with_signals

def example_backtest(df_with_signals):
    """回测示例"""
    print("\n=== 策略回测示例 ===")
    
    # 创建回测引擎
    engine = BacktestEngine(initial_capital=100000)
    
    # 运行回测
    print("运行回测...")
    results = engine.run_backtest(df_with_signals)
    
    # 显示回测结果
    print("\n回测结果:")
    print(f"初始资金: ¥{results['initial_capital']:,.2f}")
    print(f"最终资产: ¥{results['final_value']:,.2f}")
    print(f"总收益率: {results['total_return']:.2%}")
    print(f"交易次数: {results['total_trades']}")
    print(f"胜率: {results['win_rate']:.2%}")
    print(f"最大回撤: {results['max_drawdown']:.2%}")
    print(f"夏普比率: {results['sharpe_ratio']:.2f}")
    
    # 显示部分交易记录
    if results['trades']:
        print("\n最近的交易记录:")
        for trade in results['trades'][-5:]:
            action = "买入" if trade['type'] == 'buy' else "卖出"
            print(f"  {trade['date']}: {action} {trade['shares']}股 @ ¥{trade['price']:.2f}")

def main():
    """主函数"""
    print("=" * 50)
    print("AI炒股大师 - 使用示例")
    print("=" * 50)
    
    try:
        # 1. 数据采集
        df = example_data_collection()
        
        if df.empty:
            print("无法获取数据，请检查网络连接")
            return
        
        # 2. 技术分析
        df_with_signals = example_technical_analysis(df)
        
        # 3. 策略回测
        example_backtest(df_with_signals)
        
        print("\n" + "=" * 50)
        print("示例运行完成！")
        print("\n提示:")
        print("1. 运行 ./start.sh 启动Web服务")
        print("2. 访问 http://localhost:8000/docs 查看API文档")
        print("3. 使用 test_api.py 测试API功能")
        
    except Exception as e:
        print(f"\n错误: {e}")
        print("请确保网络连接正常，并且已安装所有依赖")

if __name__ == "__main__":
    main()