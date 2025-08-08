# -*- coding: utf-8 -*-
"""
数据采集模块
"""
from .tushare_collector import TushareCollector
from .akshare_collector import AkShareCollector
from .base import BaseCollector

__all__ = [
    'TushareCollector',
    'AkShareCollector',
    'BaseCollector'
]