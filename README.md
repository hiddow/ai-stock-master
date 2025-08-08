# AI炒股大师 - A股智能分析系统

## 项目简介

AI炒股大师是一个基于人工智能的A股分析系统，集成了Google Gemini AI大模型，专注于为投资者提供智能数据分析、技术指标计算、AI预测等功能，帮助用户做出更明智的投资决策。

**注意**：本系统仅供学习和研究使用，不提供实盘交易功能，所有分析结果仅供参考，不构成投资建议。

## 主要功能

### 核心功能
- 📊 **数据采集**：自动获取A股实时和历史数据
- 📈 **技术分析**：计算各类技术指标（MACD、RSI、布林带、KDJ等）
- 🤖 **AI预测**：基于机器学习的股价预测和趋势分析
- 📋 **基本面分析**：财务数据分析和价值评估
- 📰 **情绪分析**：新闻和公告的情绪影响分析
- 🔄 **策略回测**：历史数据回测验证策略效果
- 📱 **可视化界面**：直观的Web界面展示分析结果

### Gemini AI 集成功能
- 🧠 **Gemini 2.5 Pro**：深度股票分析，提供全面的投资建议
- ⚡ **Gemini 2.5 Flash**：快速分析和实时信号生成
- 📊 **智能图表分析**：上传K线图进行AI形态识别
- 💬 **AI投资顾问**：与Gemini对话获取专业投资建议
- 🔔 **智能监控警报**：自动识别异动并发出提醒

## 技术栈

- **后端**：Python 3.10+, FastAPI, Uvicorn
- **数据处理**：pandas, numpy
- **机器学习**：TensorFlow, scikit-learn, XGBoost
- **AI模型**：Google Gemini 2.5 Pro/Flash
- **数据源**：Tushare, akshare
- **数据库**：SQLite, SQLAlchemy
- **前端**：React 18, Ant Design, ECharts, Vite

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 16+
- uv (Python包管理工具)

### 安装步骤

1. 克隆项目
```bash
git clone https://github.com/yourusername/ai-stock-master.git
cd ai-stock-master
```

2. 创建虚拟环境并安装依赖
```bash
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv sync
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，添加必要的配置
```

必须配置的环境变量：
- `GEMINI_API_KEY`: Google Gemini API密钥
- `TUSHARE_TOKEN`: Tushare数据源token（可选）

4. 初始化数据库
```bash
python backend/init_db.py
```

5. 启动服务
```bash
# 启动后端服务（端口 8008）
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8008

# 启动前端（另开终端，端口 3002）
cd frontend
npm install
npm start
```

6. 访问系统
打开浏览器访问 http://localhost:3002

## 项目结构

```
AI炒股大师/
├── backend/                 # 后端服务
│   ├── data_collector/     # 数据采集模块
│   ├── ai_models/         # AI模型
│   │   ├── gemini_analyzer.py  # Gemini AI分析器
│   │   └── simple_predictor.py # 基础预测模型
│   ├── analysis/          # 分析引擎
│   │   ├── technical_analysis.py # 技术指标计算
│   │   └── backtest.py          # 回测引擎
│   ├── api/              # API接口
│   │   ├── stock.py     # 股票数据API
│   │   ├── analysis.py  # 分析API
│   │   ├── gemini.py    # Gemini AI API
│   │   └── watchlist.py # 自选股API
│   ├── database/         # 数据库模型
│   ├── config.py        # 配置管理
│   └── main.py         # 应用入口
├── frontend/            # 前端界面
│   ├── src/
│   │   ├── pages/      # 页面组件
│   │   │   ├── Dashboard.jsx      # 仪表盘
│   │   │   ├── StockList.jsx      # 股票列表
│   │   │   ├── StockDetail.jsx    # 股票详情
│   │   │   ├── Analysis.jsx       # 技术分析
│   │   │   ├── GeminiAnalysis.jsx # Gemini AI分析
│   │   │   ├── AIPredict.jsx      # AI预测
│   │   │   ├── Backtest.jsx       # 策略回测
│   │   │   └── WatchList.jsx      # 自选股
│   │   └── App.jsx     # 应用主组件
│   └── vite.config.js  # Vite配置
├── data/                # 数据存储
│   ├── raw/            # 原始数据
│   ├── processed/      # 处理后数据
│   └── stock.db       # SQLite数据库
├── tests/              # 测试文件
├── docs/               # 文档
├── pyproject.toml      # Python项目配置
├── package.json        # Node.js项目配置
└── .env.example       # 环境变量示例
```

## 使用说明

### 数据采集

系统支持从Tushare和akshare获取A股数据：
- 股票日K线数据
- 实时行情数据
- 财务报表数据
- 公司基本信息

### AI模型

#### 基础模型
1. **LSTM价格预测**：预测未来股价走势
2. **XGBoost涨跌分类**：预测股票涨跌概率
3. **情绪分析模型**：分析新闻对股价的影响

#### Gemini AI模型
1. **综合分析**：技术面、基本面、趋势预测全方位分析
2. **图表识别**：K线形态、支撑阻力位智能识别
3. **实时信号**：买卖点提示、风险警报
4. **批量分析**：同时分析多只股票，快速筛选机会

### API接口

#### 股票数据API
- `GET /api/stock/list` - 获取股票列表
- `GET /api/stock/{code}` - 获取股票详情
- `GET /api/stock/{code}/kline` - 获取K线数据
- `GET /api/stock/{code}/realtime` - 获取实时行情

#### 分析API
- `GET /api/analysis/{code}/technical` - 技术指标分析
- `POST /api/analysis/{code}/predict` - AI价格预测
- `GET /api/analysis/{code}/financial` - 财务分析

#### Gemini AI API
- `POST /api/gemini/{code}/comprehensive` - 综合分析
- `POST /api/gemini/chart-analysis` - 图表分析
- `POST /api/gemini/{code}/quick-signal` - 快速信号
- `POST /api/gemini/batch-analyze` - 批量分析
- `GET /api/gemini/monitor/alerts` - 监控警报
- `POST /api/gemini/ask` - AI问答

## 配置说明

### 环境变量 (.env)

```env
# Gemini AI配置（必需）
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL_MAIN=gemini-2.5-pro
GEMINI_MODEL_FAST=gemini-2.5-flash

# Tushare配置（可选）
TUSHARE_TOKEN=your_tushare_token_here

# 数据库配置
DATABASE_URL=sqlite:///./data/stock.db

# API配置
API_HOST=0.0.0.0
API_PORT=8008

# 前端配置
FRONTEND_PORT=3002

# 数据更新配置
UPDATE_INTERVAL=3600  # 秒
```

### 获取API密钥

#### Gemini API密钥
1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 创建新的API密钥
3. 将密钥添加到 `.env` 文件

#### Tushare Token（可选）
1. 注册 [Tushare](https://tushare.pro/register)
2. 获取你的token
3. 将token添加到 `.env` 文件

## 开发指南

### 安装开发依赖

```bash
uv sync --dev
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

### 添加新功能

1. 后端开发
   - 在 `backend/api/` 添加新的API路由
   - 在 `backend/ai_models/` 添加新的AI模型
   - 在 `backend/analysis/` 添加新的分析算法

2. 前端开发
   - 在 `frontend/src/pages/` 添加新页面
   - 使用Ant Design组件保持UI一致性
   - 使用ECharts进行数据可视化

## 注意事项

1. **数据源限制**
   - Tushare需要注册获取token，部分数据有调用次数限制
   - Akshare免费但数据可能有延迟
   - Gemini API有每分钟请求限制

2. **计算资源**
   - AI模型训练需要较大的计算资源
   - 建议使用GPU加速深度学习模型
   - 批量分析时注意控制并发数

3. **数据延迟**
   - 免费数据源可能有15分钟延迟
   - 实时数据仅供参考，不适合高频交易

4. **投资风险**
   - 本系统仅供研究学习，投资有风险，决策需谨慎
   - AI预测不保证准确性，仅供参考

## 常见问题

### Q: Gemini API调用失败？
A: 检查API密钥是否正确，网络是否能访问Google服务

### Q: 数据更新不及时？
A: 检查数据源配置，可能是API限制或网络问题

### Q: 前端无法连接后端？
A: 确保后端运行在8008端口，前端proxy配置正确

## 贡献指南

欢迎提交Issue和Pull Request！

提交PR前请确保：
1. 代码通过所有测试
2. 遵循项目代码规范
3. 更新相关文档

## 许可证

MIT License

## 联系方式

如有问题，请提交Issue或联系作者。

---

**免责声明**：本项目仅供学习和研究使用，不构成任何投资建议。股市有风险，投资需谨慎。作者不对使用本系统造成的任何损失负责。