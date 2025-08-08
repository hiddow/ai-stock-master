#!/bin/bash

echo "AI炒股大师 - 前端启动脚本"
echo "========================="

# 检查后端服务是否运行
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "⚠️  后端服务未启动，请先运行后端服务："
    echo "   ./start.sh"
    echo ""
fi

# 启动前端
echo "启动前端服务..."
echo "访问 http://localhost:3002 查看界面"
echo ""
echo "按 Ctrl+C 停止服务"

cd frontend
npm run start