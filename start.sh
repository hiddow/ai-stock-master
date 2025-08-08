#!/bin/bash

echo "AI炒股大师 - 启动脚本"
echo "====================="

# 激活虚拟环境
source .venv/bin/activate

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "创建.env文件..."
    cp .env.example .env
    echo "请编辑.env文件，添加您的Tushare Token（如果需要）"
fi

# 初始化数据库
echo "初始化数据库..."
python backend/init_db.py

# 启动后端服务
echo "启动后端服务..."
echo "访问 http://localhost:8000 查看API"
echo "访问 http://localhost:8000/docs 查看API文档"
echo ""
echo "按 Ctrl+C 停止服务"
python backend/main.py