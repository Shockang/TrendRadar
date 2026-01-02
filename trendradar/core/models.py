# coding=utf-8
"""
TrendRadar 数据模型
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class NewsConfig:
    """新闻配置"""
    platforms: List[Dict[str, str]] = field(default_factory=list)
    request_interval: int = 1000
    timezone: str = "Asia/Shanghai"
    report_mode: str = "daily"
    rank_threshold: int = 5
    use_proxy: bool = False
    proxy_url: str = ""
    enable_notification: bool = False

    # 权重配置
    rank_weight: float = 0.6
    frequency_weight: float = 0.3
    hotness_weight: float = 0.1

    # 存储配置
    storage_backend: str = "local"
    storage_dir: str = "output"
    enable_sqlite: bool = True
    enable_txt: bool = False
    enable_html: bool = True
    retention_days: int = 0


@dataclass
class NewsItem:
    """单条新闻"""
    title: str
    platform: str
    platform_id: str
    url: str = ""
    mobile_url: str = ""
    rank: int = 0
    time: str = ""
    date: str = ""

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "title": self.title,
            "platform": self.platform,
            "platform_id": self.platform_id,
            "url": self.url,
            "mobile_url": self.mobile_url,
            "rank": self.rank,
            "time": self.time,
            "date": self.date,
        }


@dataclass
class NewsData:
    """新闻数据集合"""
    date: str
    time: str
    items: List[NewsItem] = field(default_factory=list)
    platforms: Dict[str, str] = field(default_factory=dict)
    failed_platforms: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "date": self.date,
            "time": self.time,
            "items": [item.to_dict() for item in self.items],
            "platforms": self.platforms,
            "failed_platforms": self.failed_platforms,
        }


@dataclass
class TopicStat:
    """话题统计"""
    keywords: List[str]
    count: int
    titles: List[Dict] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "keywords": self.keywords,
            "count": self.count,
            "titles": self.titles,
        }
