# coding=utf-8
"""
TrendRadar API - 简化的集成接口

热点新闻聚合与分析工具的核心API，方便集成到现有工程中。
"""

from .core.api import TrendRadarAPI
from .core.models import NewsData, NewsConfig

__version__ = "1.0.0"
__all__ = ["TrendRadarAPI", "NewsData", "NewsConfig"]
