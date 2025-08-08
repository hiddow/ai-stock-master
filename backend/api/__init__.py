# -*- coding: utf-8 -*-
"""
API路由模块
"""
from .stock import router as stock_router
from .analysis import router as analysis_router
from .data import router as data_router
from .watchlist import router as watchlist_router
from .gemini import router as gemini_router

__all__ = [
    'stock_router',
    'analysis_router',
    'data_router',
    'watchlist_router',
    'gemini_router'
]