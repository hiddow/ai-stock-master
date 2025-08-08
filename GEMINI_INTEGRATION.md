# Gemini AI 集成文档

## 概述

本文档详细介绍AI炒股大师系统中Google Gemini AI的集成方案，包括架构设计、功能实现、API接口和使用指南。

## 架构设计

### 双模型架构

系统采用双模型架构，充分利用不同模型的优势：

1. **Gemini 2.5 Pro（主分析模型）**
   - 用于深度股票分析
   - 提供全面的投资建议
   - 支持复杂的多维度分析
   - 适合需要深入理解的场景

2. **Gemini 2.5 Flash（快速分析模型）**
   - 用于实时信号生成
   - 快速响应用户查询
   - 批量股票筛选
   - 适合需要快速反馈的场景

### 模块结构

```
backend/ai_models/
├── gemini_analyzer.py      # Gemini分析器核心模块
│   ├── GeminiAnalyzer     # 主分析器类
│   └── GeminiFastAnalyzer # 快速分析器类
└── __init__.py            # 模块导出
```

## 核心功能

### 1. 综合股票分析

```python
def analyze_stock_comprehensive(code, stock_data, technical_indicators, financial_data)
```

**功能说明**：
- 结合技术面和基本面进行全方位分析
- 提供短期（1-5天）和中期（1-4周）预测
- 生成买入/持有/卖出建议
- 识别关键支撑位和阻力位

**分析维度**：
- 技术面：趋势、形态、指标信号
- 基本面：财务状况、估值水平
- 市场面：成交量、资金流向
- 风险面：潜在风险、止损建议

### 2. K线图形态识别

```python
def analyze_chart_pattern(chart_image)
```

**功能说明**：
- 支持上传K线图进行AI分析
- 识别经典技术形态（头肩顶、双底、三角形等）
- 标注支撑位和阻力位
- 生成形态交易建议

**识别形态**：
- 反转形态：头肩顶/底、双顶/底、三重顶/底
- 持续形态：三角形、旗形、楔形
- K线组合：锤子线、吞没形态、十字星

### 3. 快速交易信号

```python
def quick_signal(code, latest_data)
```

**功能说明**：
- 实时生成交易信号
- 信号强度评分（1-10）
- 简明扼要的操作理由
- 适合日内交易决策

**信号类型**：
- BUY：买入信号
- HOLD：持有观望
- SELL：卖出信号

### 4. 新闻情绪分析

```python
def analyze_news_sentiment(news_list)
```

**功能说明**：
- 分析新闻对股价的潜在影响
- 情绪评分（-100到+100）
- 识别利好利空因素
- 预测市场反应

### 5. 批量股票分析

```python
def batch_analyze(stock_list)
```

**功能说明**：
- 同时分析多只股票
- 快速筛选投资机会
- 生成优先级排序
- 支持自定义筛选条件

### 6. 实时监控警报

```python
def monitor_realtime(stock_list)
```

**功能说明**：
- 监控股票异动
- 自动触发警报
- 支持多种警报类型
- 实时推送通知

**警报类型**：
- PRICE_CHANGE：价格异动（涨跌超过5%）
- VOLUME_SPIKE：成交量异常（超过平均2倍）
- BREAKOUT：突破关键价位
- PATTERN_FORMED：形成重要技术形态

## API接口文档

### 基础URL
```
http://localhost:8008/api/gemini
```

### 接口列表

#### 1. 综合分析
```http
POST /api/gemini/{code}/comprehensive
```

**请求参数**：
- `code`：股票代码（路径参数）
- `days`：分析天数（查询参数，默认30）

**响应示例**：
```json
{
  "status": "success",
  "stock": {
    "code": "600036",
    "name": "招商银行"
  },
  "gemini_analysis": {
    "status": "success",
    "model": "gemini-2.5-pro",
    "analysis": {
      "technical_analysis": {
        "trend": "上升趋势",
        "support": 38.5,
        "resistance": 42.0
      },
      "short_term_prediction": {
        "direction": "看涨",
        "target": 41.5,
        "probability": 0.72
      },
      "recommendation": "买入",
      "risk_level": "中等",
      "stop_loss": 37.8
    }
  }
}
```

#### 2. 图表分析
```http
POST /api/gemini/chart-analysis
```

**请求参数**：
- `file`：K线图图片文件（multipart/form-data）

**响应示例**：
```json
{
  "status": "success",
  "chart_analysis": {
    "trend": "震荡上行",
    "patterns": ["上升三角形", "金叉"],
    "support_levels": [38.5, 37.2],
    "resistance_levels": [41.0, 42.5],
    "signals": ["突破信号待确认"],
    "recommendation": "逢低买入"
  }
}
```

#### 3. 快速信号
```http
POST /api/gemini/{code}/quick-signal
```

**请求参数**：
- `code`：股票代码（路径参数）

**响应示例**：
```json
{
  "status": "success",
  "code": "600036",
  "signal": "BUY",
  "strength": 7,
  "reason": "RSI超卖反弹，MACD金叉形成，量能配合良好",
  "timestamp": "2024-01-20T10:30:00"
}
```

#### 4. 批量分析
```http
POST /api/gemini/batch-analyze
```

**请求参数**：
```json
{
  "codes": ["600036", "000001", "002415"]
}
```

**响应示例**：
```json
{
  "status": "success",
  "analyzed_count": 3,
  "results": [
    {
      "code": "600036",
      "signal": "BUY",
      "strength": 8,
      "reason": "技术面向好，资金流入"
    },
    {
      "code": "000001",
      "signal": "HOLD",
      "strength": 5,
      "reason": "震荡整理，等待方向"
    }
  ]
}
```

#### 5. 监控警报
```http
GET /api/gemini/monitor/alerts
```

**响应示例**：
```json
{
  "status": "success",
  "alerts": [
    {
      "code": "600036",
      "name": "招商银行",
      "alert_type": "PRICE_CHANGE",
      "change_pct": 5.8,
      "signal": "BUY",
      "reason": "突破前高，量能放大"
    },
    {
      "code": "000002",
      "name": "万科A",
      "alert_type": "VOLUME_SPIKE",
      "volume_ratio": 2.5
    }
  ],
  "monitored_stocks": 100,
  "timestamp": "2024-01-20T10:30:00"
}
```

#### 6. AI问答
```http
POST /api/gemini/ask
```

**请求参数**：
```json
{
  "question": "招商银行最近的走势如何？",
  "context": {
    "code": "600036",
    "price": 40.5,
    "change_pct": 2.3
  }
}
```

**响应示例**：
```json
{
  "status": "success",
  "question": "招商银行最近的走势如何？",
  "answer": "招商银行（600036）近期表现强势，目前价格40.5元，今日涨幅2.3%。从技术面看，股价突破了前期压力位40元，成交量温和放大，MACD指标金叉向上，显示上涨动能充足。建议关注42元附近的压力位，如能有效突破，有望开启新一轮上涨行情。",
  "model": "gemini-2.5-flash",
  "timestamp": "2024-01-20T10:30:00"
}
```

## 配置指南

### 环境变量配置

在 `.env` 文件中配置：

```env
# Gemini API配置
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL_MAIN=gemini-2.5-pro
GEMINI_MODEL_FAST=gemini-2.5-flash

# 可选：调整模型参数
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=500
```

### 获取API密钥

1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 登录Google账号
3. 点击"Create API Key"
4. 选择项目或创建新项目
5. 复制生成的API密钥
6. 将密钥添加到 `.env` 文件

### 模型选择建议

| 场景 | 推荐模型 | 原因 |
|------|---------|------|
| 深度分析 | Gemini 2.5 Pro | 更强的理解和推理能力 |
| 实时信号 | Gemini 2.5 Flash | 响应速度快，成本低 |
| 批量筛选 | Gemini 2.5 Flash | 可以快速处理大量请求 |
| 复杂问答 | Gemini 2.5 Pro | 更准确的回答质量 |
| 图表识别 | Gemini 2.5 Flash | 视觉识别能力足够 |

## 使用示例

### Python调用示例

```python
from backend.ai_models import GeminiAnalyzer

# 初始化分析器
analyzer = GeminiAnalyzer()

# 综合分析
result = analyzer.analyze_stock_comprehensive(
    code="600036",
    stock_data=df,  # pandas DataFrame
    technical_indicators={
        "rsi": 45,
        "macd": 0.15,
        "ma5": 40.2,
        "ma20": 39.8
    },
    financial_data={
        "pe": 5.8,
        "roe": 15.2,
        "revenue": 1500
    }
)

print(result["analysis"])
```

### 前端调用示例

```javascript
// 获取快速信号
async function getQuickSignal(code) {
  const response = await fetch(`/api/gemini/${code}/quick-signal`, {
    method: 'POST'
  });
  const data = await response.json();
  
  if (data.signal === 'BUY') {
    console.log(`买入信号：${data.reason}`);
  }
}

// 上传图表分析
async function analyzeChart(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('/api/gemini/chart-analysis', {
    method: 'POST',
    body: formData
  });
  const data = await response.json();
  
  console.log('识别的形态：', data.chart_analysis.patterns);
}
```

## 性能优化

### 1. 缓存策略
- 缓存常用分析结果15分钟
- 相同请求避免重复调用API
- 使用Redis存储缓存（可选）

### 2. 并发控制
- 限制同时进行的API调用数
- 使用队列管理批量请求
- 设置合理的超时时间

### 3. 成本控制
- 监控API使用量
- 对非关键功能使用Flash模型
- 实施用户配额限制

## 错误处理

### 常见错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 401 | API密钥无效 | 检查密钥配置 |
| 429 | 请求频率过高 | 实施限流策略 |
| 500 | 服务器错误 | 检查日志，重试请求 |
| 503 | 服务不可用 | 检查网络，稍后重试 |

### 错误处理示例

```python
try:
    result = analyzer.analyze_stock_comprehensive(code, data)
except Exception as e:
    logger.error(f"Gemini分析失败: {e}")
    # 降级到基础分析
    result = fallback_analysis(code, data)
```

## 安全建议

1. **API密钥安全**
   - 不要将密钥提交到代码仓库
   - 使用环境变量管理密钥
   - 定期轮换密钥

2. **数据隐私**
   - 不要发送敏感用户信息
   - 遵守数据保护法规
   - 实施数据脱敏

3. **访问控制**
   - 实施用户认证
   - 设置API访问权限
   - 记录所有API调用

## 未来扩展

### 计划中的功能
1. 支持更多Gemini模型
2. 实现对话式投资顾问
3. 加入多模态分析（图表+文本）
4. 支持实时语音交互
5. 集成更多数据源

### 优化方向
1. 提升响应速度
2. 改进分析准确性
3. 降低API成本
4. 增强错误恢复能力

## 相关资源

- [Google AI Studio](https://makersuite.google.com/)
- [Gemini API文档](https://ai.google.dev/docs)
- [google-genai Python SDK](https://github.com/google/genai)
- [项目GitHub仓库](https://github.com/yourusername/ai-stock-master)

## 支持与反馈

如有问题或建议，请通过以下方式联系：
- GitHub Issues
- 邮件：support@example.com
- 技术论坛：[链接]

---

最后更新：2024年1月
版本：1.0.0