"""
初始化数据库
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from backend.database import Base, engine
from backend.database.models import *
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """初始化数据库，创建所有表"""
    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("数据库初始化成功")
        logger.info(f"创建的表: {', '.join(Base.metadata.tables.keys())}")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise

if __name__ == "__main__":
    init_database()