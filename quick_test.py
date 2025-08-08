"""
快速测试脚本 - 验证核心功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试模块导入"""
    print("测试模块导入...")
    try:
        from backend.data_collector import AkShareCollector
        from backend.analysis import TechnicalAnalyzer, BacktestEngine
        from backend.ai_models import SimplePricePredictor, PatternRecognizer
        from backend.database import Base, engine
        print("✓ 所有模块导入成功")
        return True
    except Exception as e:
        print(f"✗ 模块导入失败: {e}")
        return False

def test_database():
    """测试数据库连接"""
    print("\n测试数据库...")
    try:
        from backend.database import SessionLocal, Stock
        db = SessionLocal()
        count = db.query(Stock).count()
        print(f"✓ 数据库连接成功，当前有 {count} 只股票")
        db.close()
        return True
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        return False

def test_technical_analysis():
    """测试技术分析功能"""
    print("\n测试技术分析...")
    try:
        from backend.analysis import TechnicalAnalyzer
        import pandas as pd
        import numpy as np
        
        # ��建模拟数据
        dates = pd.date_range(start='2024-01-01', periods=30)
        data = {
            'date': dates,
            'open': np.random.uniform(10, 11, 30),
            'high': np.random.uniform(11, 12, 30),
            'low': np.random.uniform(9, 10, 30),
            'close': np.random.uniform(10, 11, 30),
            'volume': np.random.uniform(1000000, 2000000, 30)
        }
        df = pd.DataFrame(data)
        
        analyzer = TechnicalAnalyzer()
        result = analyzer.calculate_ma(df, periods=[5, 10])
        
        if 'ma5' in result.columns and 'ma10' in result.columns:
            print("✓ 技术指标计算成功")
            return True
        else:
            print("✗ 技术指标计算失败")
            return False
    except Exception as e:
        print(f"✗ 技术分析测试失败: {e}")
        return False

def test_ai_model():
    """测试AI模型"""
    print("\n测试AI预测模型...")
    try:
        from backend.ai_models import SimplePricePredictor
        import pandas as pd
        import numpy as np
        
        # 创建模拟数据
        dates = pd.date_range(start='2024-01-01', periods=30)
        data = {
            'date': dates,
            'open': np.random.uniform(10, 11, 30),
            'high': np.random.uniform(11, 12, 30),
            'low': np.random.uniform(9, 10, 30),
            'close': np.random.uniform(10, 11, 30),
            'volume': np.random.uniform(1000000, 2000000, 30)
        }
        df = pd.DataFrame(data)
        
        predictor = SimplePricePredictor()
        result = predictor.predict_next_day(df)
        
        if result and 'prediction' in result:
            print(f"✓ AI预测成功: 预测价格 {result.get('prediction', 'N/A'):.2f}")
            return True
        else:
            print("✗ AI预测失败")
            return False
    except Exception as e:
        print(f"✗ AI模型测试失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("AI炒股大师 - 快速功能测试")
    print("=" * 50)
    
    tests = [
        ("模块导入", test_imports),
        ("数据库连接", test_database),
        ("技术分析", test_technical_analysis),
        ("AI预测模型", test_ai_model),
    ]
    
    results = []
    for name, test_func in tests:
        success = test_func()
        results.append((name, success))
    
    print("\n" + "=" * 50)
    print("测试结果:")
    for name, success in results:
        status = "✓" if success else "✗"
        print(f"  {status} {name}")
    
    all_passed = all(success for _, success in results)
    if all_passed:
        print("\n✅ 所有测试通过！")
        print("\n下一步:")
        print("1. 运行 ./start.sh 启动Web服务")
        print("2. 访问 http://localhost:8000/docs 查看API文档")
        print("3. 运行 python example.py 查看完整示例（需要网络）")
    else:
        print("\n❌ 部分测试失败，请检查错误信息")
    
    print("=" * 50)

if __name__ == "__main__":
    main()