# AI炒股大师 - A股智能分析系统

## 项目简介

AI炒股大师是一个基于人工智能的A股分析系统，专注于为投资者提供数据分析、技术指标计算、AI预测等功能，帮助用户做出更明智的投资决策。

**注意**：本系统仅供学习和研究使用，不提供实盘交易功能，所有分析结果仅供参考，不构成投资建议。

## 主要功能

- 📊 **数据采集**：自动获取A股实时和历史数据
- 📈 **技术分析**：计算各类技术指标（MACD、RSI、布林带等）
- 🤖 **AI预测**：基于机器学习的股价预测和趋势分析
- 📋 **基本面分析**：财务数据分析和价值评估
- 📰 **情绪分析**：新闻和公告的情绪影响分析
- 🔄 **策略回测**：历史数据回测验证策略效果
- 📱 **可视化界面**：直观的Web界面展示分析结果

## 技术栈

- **后端**：Python 3.10+, FastAPI
- **数据处理**：pandas, numpy
- **机器学习**：TensorFlow, scikit-learn, XGBoost
- **数据源**：Tushare, akshare
- **数据库**：SQLite
- **前端**：React, ECharts

## 快速开始

### 环境要求

- Python 3.10+
- uv (Python包管理工具)

### 安装步骤

1. 克隆项目
```bash
git clone https://github.com/hiddow/ai-stock-master.git
cd ai-stock-master
```

2. 创建虚拟环境并安装依赖
```bash
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .
```

3. 配置数据源
```bash
cp .env.example .env
# 编辑 .env 文件，添加你的Tushare token
```

4. 初始化数据库
```bash
python backend/init_db.py
```

5. 启动服务
```bash
# 启动后端服务
uvicorn backend.main:app --reload

# 启动前端（另开终端）
cd frontend
npm install
npm run dev
```

## 项目结构

```
AI炒股大师/
├── backend/                 # 后端服务
│   ├── data_collector/     # 数据采集模块
│   ├── ai_models/         # AI模型
│   ├── analysis/          # 分析引擎
│   └── api/              # API接口
├── frontend/             # 前端界面
│   └── dashboard/        # 数据可视化
├── data/                 # 数据存储
│   ├── raw/             # 原始数据
│   └── processed/       # 处理后数据
├── config/              # 配置文件
├── tests/               # 测试文件
└── docs/                # 文档
```

## 使用说明

### 数据采集

系统会自动从Tushare和akshare获取A股数据，包括：
- 股票日K线数据
- 实时行情数据
- 财务报表数据
- 公司基本信息

### AI模型

系统提供多种AI模型：
1. **LSTM价格预测**：预测未来股价走势
2. **XGBoost涨跌分类**：预测股票涨跌概率
3. **情绪分析模型**：分析新闻对股价的影响
4. **价值评估模型**：基于基本面的价值打分

### API接口

主要API端点：
- `GET /api/stocks/list` - 获取股票列表
- `GET /api/stocks/{code}/kline` - 获取K线数据
- `POST /api/analysis/technical` - 技术指标分析
- `POST /api/predict/price` - AI价格预测
- `GET /api/backtest/run` - 运行回测

## 配置说明

### 环境变量 (.env)

```env
# Tushare配置
TUSHARE_TOKEN=your_token_here

# 数据库配置
DATABASE_URL=sqlite:///./data/stock.db

# API配置
API_HOST=0.0.0.0
API_PORT=8000

# 数据更新配置
UPDATE_INTERVAL=3600  # 秒
```

## 开发指南

### 安装开发依赖

```bash
uv pip install -e ".[dev]"
```

### 运行测试

```bash
pytest tests/
```

### 代码格式化

```bash
black backend/
ruff check backend/
```

## 注意事项

1. **数据源限制**：Tushare需要注册获取token，部分数据有调用次数限制
2. **计算资源**：AI模型训练需要较大的计算资源
3. **数据延迟**：免费数据源可能有15分钟延迟
4. **投资风险**：本系统仅供研究学习，投资有风险，决策需谨慎

## 贡献指南

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 联系方式

如有问题，请提交Issue或联系作者。

---

**免责声明**：本项目仅供学习和研究使用，不构成任何投资建议。股市有风险，投资需谨慎。