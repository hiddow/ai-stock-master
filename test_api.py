"""
测试脚本 - 测试AI炒股大师基本功能
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    response = requests.get(f"{BASE_URL}/health")
    print("健康检查:", response.json())
    return response.status_code == 200

def test_update_stock_list():
    """测试更新股票列表"""
    response = requests.post(f"{BASE_URL}/api/data/update/stock-list")
    print("更新股票列表:", response.json())
    return response.status_code == 200

def test_get_stock_list():
    """测试获取股票列表"""
    response = requests.get(f"{BASE_URL}/api/stock/list")
    data = response.json()
    print(f"获取股票列表: 共{len(data)}只股票")
    if data:
        print("示例股票:", data[:3])
    return response.status_code == 200

def test_get_stock_daily(code="000001"):
    """测试获取股票日线数据"""
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
    
    response = requests.get(
        f"{BASE_URL}/api/stock/{code}/daily",
        params={"start_date": start_date, "end_date": end_date}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"获取{code}日线数据: 共{len(data)}条")
        if data:
            print("最新数据:", data[-1])
    else:
        print(f"获取日线数据失败: {response.status_code}")
    
    return response.status_code == 200

def test_technical_analysis(code="000001"):
    """测试技术指标分析"""
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=60)).strftime("%Y%m%d")
    
    response = requests.post(
        f"{BASE_URL}/api/analysis/{code}/technical",
        params={"start_date": start_date, "end_date": end_date}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"技术分析结果:")
        print(f"  - 代码: {data['code']}")
        print(f"  - 周期: {data['period']}")
        print(f"  - 最新信号: {data.get('latest_signal', 'N/A')}")
        print(f"  - 信号强度: {data.get('signal_strength', 'N/A')}")
    else:
        print(f"技术分析失败: {response.status_code}")
    
    return response.status_code == 200

def test_backtest(code="000001"):
    """测试回测功能"""
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=180)).strftime("%Y%m%d")
    
    response = requests.post(
        f"{BASE_URL}/api/analysis/{code}/backtest",
        params={
            "start_date": start_date,
            "end_date": end_date,
            "initial_capital": 100000
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"回测结果:")
        print(f"  - {data['summary']}")
        metrics = data['metrics']
        print(f"  - 交易次数: {metrics['total_trades']}")
        print(f"  - 胜率: {metrics['win_rate']:.2%}")
        print(f"  - 最大回撤: {metrics['max_drawdown']:.2%}")
    else:
        print(f"回测失败: {response.status_code}")
    
    return response.status_code == 200

def main():
    """运行所有测试"""
    print("=" * 50)
    print("AI炒股大师功能测试")
    print("=" * 50)
    
    tests = [
        ("健康检查", test_health),
        ("更新股票列表", test_update_stock_list),
        ("获取股票列表", test_get_stock_list),
        ("获取日线数据", test_get_stock_daily),
        ("技术指标分析", test_technical_analysis),
        ("策略回测", test_backtest),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n测试: {name}")
        print("-" * 30)
        try:
            success = test_func()
            results.append((name, "✓" if success else "✗"))
        except Exception as e:
            print(f"错误: {e}")
            results.append((name, "✗"))
    
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    for name, status in results:
        print(f"  {status} {name}")
    print("=" * 50)

if __name__ == "__main__":
    print("请确保后端服务已启动 (运行: python backend/main.py)")
    print("按Enter继续...")
    input()
    main()