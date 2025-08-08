"""
FastAPI主应用
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from backend.config import settings
from backend.api import stock_router, analysis_router, data_router, watchlist_router, gemini_router

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("AI炒股大师启动中...")
    yield
    # 关闭时执行
    logger.info("AI炒股大师关闭中...")

# 创建FastAPI应用
app = FastAPI(
    title="AI炒股大师",
    description="A股智能分析系统API",
    version="0.1.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(stock_router, prefix="/api/stock", tags=["股票"])
app.include_router(analysis_router, prefix="/api/analysis", tags=["分析"])
app.include_router(data_router, prefix="/api/data", tags=["数据"])
app.include_router(watchlist_router, prefix="/api/watchlist", tags=["关注列表"])
app.include_router(gemini_router, prefix="/api/gemini", tags=["Gemini AI"])

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用AI炒股大师",
        "version": "0.1.0",
        "api_docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )