# AI炒股大师 - 快速启动指南

## 🚀 一键启动

### 1. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，添加你的 Gemini API 密钥
```

### 2. 启动后端服务
```bash
# 使用 uv 安装依赖并启动
uv sync
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8008
```
后端服务将运行在 http://localhost:8008

### 3. 启动前端界面（新开终端窗口）
```bash
cd frontend
npm install  # 首次运行需要安装依赖
npm start
```
前端界面将运行在 http://localhost:3002

## 📱 访问系统

打开浏览器访问：http://localhost:3002

## 🎯 功能导航

### 核心功能
1. **仪表盘** - 市场概览、热门股票、最新信号
2. **股票列表** - 浏览、搜索、收藏股票
3. **技术分析** - K线图、技术指标、买卖信号
4. **AI预测** - 智能预测、形态识别、趋势分析
5. **策略回测** - 历史回测、收益分析、风险评估
6. **自选股** - 管理关注的股票列表

### Gemini AI功能
7. **Gemini AI分析** - 全新AI分析页面
   - 快速信号：实时买卖建议
   - 监控警报：异动股票提醒
   - 综合分析：深度股票分析
   - AI问答：智能投资顾问

## 🔧 常用操作

### 选择股票进行分析
1. 在"股票列表"页面点击任意股票
2. 系统自动跳转到"技术分析"页面
3. 可切换到"AI预测"或"Gemini AI分析"查看更多分析

### 使用Gemini AI分析
1. 进入"Gemini AI分析"页面
2. 输入股票代码（如：600036）
3. 点击各个分析按钮：
   - "获取快速信号" - 快速交易建议
   - "综合分析" - 全面深度分析
   - "上传K线图" - AI图表形态识别
4. 在底部AI问答区域直接提问

### 收藏股票到自选
- 点击股票列表中的星号图标收藏股票
- 在"自选股"页面管理收藏的股票
- 支持批量分析自选股

### 更新数据
- 点击各页面的"刷新"按钮更新最新数据
- 数据来源：AkShare（免费实时数据）
- Gemini AI提供智能分析

## ⚙️ 环境配置

### 必需配置
```env
# Gemini AI配置
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL_MAIN=gemini-2.5-pro
GEMINI_MODEL_FAST=gemini-2.5-flash
```

### 获取Gemini API密钥
1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 创建新的API密钥
3. 将密钥添加到 `.env` 文件

## ⚠️ 注意事项

1. **首次运行**
   - 需要安装依赖包，请耐心等待
   - 需要初始化数据库：`python backend/init_db.py`
   - 需要配置Gemini API密钥才能使用AI功能

2. **端口配置**
   - 后端运行在 8008 端口
   - 前端运行在 3002 端口
   - 确保这些端口未被占用

3. **数据说明**
   - 部分功能使用模拟数据展示效果
   - 实时数据来自AkShare（可能有15分钟延迟）
   - Gemini AI分析基于实时数据

4. **使用限制**
   - Gemini API有请求频率限制
   - 免费数据源有调用次数限制
   - 本系统仅供学习研究，不构成投资建议

## 🛑 停止服务

- 停止前端：在前端终端按 Ctrl+C
- 停止后端：在后端终端按 Ctrl+C

## 📊 API文档

访问 http://localhost:8008/docs 查看完整API文档

### 主要API端点
- `/api/stock/list` - 股票列表
- `/api/stock/{code}/kline` - K线数据
- `/api/analysis/{code}/technical` - 技术分析
- `/api/gemini/{code}/comprehensive` - Gemini综合分析
- `/api/gemini/{code}/quick-signal` - 快速交易信号
- `/api/gemini/ask` - AI问答

## 🐛 问题排查

### 常见问题

1. **后端启动失败**
   - 确保Python 3.10+已安装
   - 确保已激活虚拟环境
   - 检查端口8008是否被占用
   - 运行 `uv sync` 安装��赖

2. **前端启动失败**
   - 确保Node.js 16+已安装
   - 在frontend目录运行 `npm install`
   - 检查端口3002是否被占用

3. **Gemini API错误**
   - 检查API密钥是否正确
   - 确保网络能访问Google服务
   - 检查是否超过API调用限制

4. **数据加载失败**
   - 检查网络连接
   - 确认数据库已初始化
   - 查看后端日志排查错误

### 查看日志
```bash
# 后端日志
tail -f backend.log

# 前端日志
tail -f frontend/frontend.log
```

## 📚 进阶使用

### 添加更多股票数据
```python
# 使用数据采集脚本
python backend/data_collector/akshare_collector.py
```

### 自定义技术指标
在 `backend/analysis/technical_analysis.py` 中添加新指标

### 调整AI模型参数
编辑 `backend/ai_models/gemini_analyzer.py` 中的温度和输出参数

## 🎉 开始使用

现在您可以开始探索AI炒股大师的强大功能了！

记住：
- 📈 理性投资，控制风险
- 🤖 AI建议仅供参考
- 📚 持续学习，提升认知

祝您投资顺利！💰