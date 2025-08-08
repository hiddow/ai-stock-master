#!/bin/bash

echo "初始化股票数据..."
echo "=================="

# 更新股票列表
echo "1. 更新股票列表..."
curl -X POST "http://localhost:8000/api/data/update/stock-list"
echo ""

# 获取一些热门股票的数据
echo "2. 更新热门股票数据..."

# 设置日期范围（最近30天）
END_DATE=$(date +%Y%m%d)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    START_DATE=$(date -v-30d +%Y%m%d)
else
    # Linux
    START_DATE=$(date -d "-30 days" +%Y%m%d)
fi

# 热门股票列表
STOCKS=(
    "000001"  # 平安银行
    "000002"  # 万科A
    "000858"  # 五粮液
    "002415"  # 海康威视
    "600519"  # 贵州茅台
    "600036"  # 招商银行
    "000333"  # 美的集团
    "002594"  # 比亚迪
    "300750"  # 宁德时代
    "601318"  # 中国平安
    "605378"  # 野马电池
)

for stock in "${STOCKS[@]}"; do
    echo "更新 $stock ..."
    curl -X POST "http://localhost:8000/api/data/update/daily/${stock}?start_date=${START_DATE}&end_date=${END_DATE}"
    echo ""
    sleep 1  # 避免请求过快
done

echo ""
echo "✅ 数据初始化完成！"
echo "您现在可以在前端搜索和分析这些股票了。"