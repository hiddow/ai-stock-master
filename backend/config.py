"""
配置管理模块
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """应用配置"""
    
    # Tushare配置
    tushare_token: Optional[str] = Field(None, env="TUSHARE_TOKEN")
    
    # Gemini AI配置
    gemini_api_key: Optional[str] = Field(None, env="GEMINI_API_KEY")
    gemini_model_main: str = Field("gemini-2.5-pro", env="GEMINI_MODEL_MAIN")
    gemini_model_fast: str = Field("gemini-2.5-flash", env="GEMINI_MODEL_FAST")
    
    # 数据库配置
    database_url: str = Field("sqlite:///./data/stock.db", env="DATABASE_URL")
    
    # API配置
    api_host: str = Field("0.0.0.0", env="API_HOST")
    api_port: int = Field(8000, env="API_PORT")
    
    # 数据更新配置
    update_interval: int = Field(3600, env="UPDATE_INTERVAL")  # 秒
    
    # 日志配置
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    # 项目路径
    base_dir: Path = Path(__file__).parent.parent
    data_dir: Path = base_dir / "data"
    raw_data_dir: Path = data_dir / "raw"
    processed_data_dir: Path = data_dir / "processed"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 确保数据目录存在
        self.data_dir.mkdir(exist_ok=True, parents=True)
        self.raw_data_dir.mkdir(exist_ok=True, parents=True)
        self.processed_data_dir.mkdir(exist_ok=True, parents=True)

# 全局配置实例
settings = Settings()