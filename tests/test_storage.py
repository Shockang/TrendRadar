# coding=utf-8
"""
TrendRadar Storage Manager 单元测试
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from trendradar.storage import StorageManager, convert_crawl_results_to_news_data


class TestStorageManager:
    """StorageManager 测试类"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def storage(self, temp_dir):
        """创建 StorageManager 实例"""
        return StorageManager(
            backend_type="local",
            data_dir=temp_dir,
            timezone="Asia/Shanghai"
        )

    def test_init_local_backend(self, temp_dir):
        """测试本地存储初始化"""
        storage = StorageManager(
            backend_type="local",
            data_dir=temp_dir,
            timezone="Asia/Shanghai"
        )

        assert storage.get_backend() is not None
        assert storage.timezone == "Asia/Shanghai"

    def test_init_with_custom_timezone(self, temp_dir):
        """测试自定义时区"""
        storage = StorageManager(
            backend_type="local",
            data_dir=temp_dir,
            timezone="America/New_York"
        )

        assert storage.timezone == "America/New_York"

    def test_save_and_get_news_data(self, storage):
        """测试保存和获取新闻数据"""
        from trendradar.storage.base import NewsData, NewsItem

        # 创建测试数据
        news_data = NewsData(
            date="2026-01-02",
            crawl_time="12:00",
            items={
                "zhihu": [
                    NewsItem(
                        title="测试新闻",
                        source_id="zhihu",
                        url="http://example.com/1",
                        rank=1,
                        crawl_time="12:00"
                    )
                ]
            }
        )

        # 保存数据
        storage.save_news_data(news_data)

        # 获取数据
        retrieved_data = storage.get_today_all_data("2026-01-02")

        assert retrieved_data is not None
        assert retrieved_data.date == "2026-01-02"
        assert "zhihu" in retrieved_data.items
        assert len(retrieved_data.items["zhihu"]) == 1
        assert retrieved_data.items["zhihu"][0].title == "测试新闻"

    def test_get_multiple_sources(self, storage):
        """测试保存多个来源的新闻"""
        from trendradar.storage.base import NewsData, NewsItem

        # 创建测试数据 - 多个来源
        news_data = NewsData(
            date="2026-01-02",
            crawl_time="12:00",
            items={
                "zhihu": [
                    NewsItem(
                        title="知乎新闻",
                        source_id="zhihu",
                        url="http://example.com/1",
                        rank=1,
                        crawl_time="12:00"
                    )
                ],
                "weibo": [
                    NewsItem(
                        title="微博新闻",
                        source_id="weibo",
                        url="http://example.com/2",
                        rank=1,
                        crawl_time="12:00"
                    )
                ]
            }
        )

        storage.save_news_data(news_data)

        # 获取所有数据
        retrieved_data = storage.get_today_all_data("2026-01-02")

        assert retrieved_data is not None
        assert "zhihu" in retrieved_data.items
        assert "weibo" in retrieved_data.items
        assert len(retrieved_data.items["zhihu"]) == 1
        assert len(retrieved_data.items["weibo"]) == 1

    def test_get_nonexistent_data(self, storage):
        """测试获取不存在的数据"""
        data = storage.get_today_all_data("2099-01-01")
        assert data is None

    def test_convert_crawl_results_to_news_data(self):
        """测试转换爬虫结果为新闻数据"""
        # 模拟爬虫结果
        results = {
            "zhihu": {
                "测试标题": {
                    "time": "12:00:00",
                    "ranks": [1],
                    "url": "http://example.com/1",
                    "mobileUrl": "http://m.example.com/1"
                }
            }
        }
        id_to_name = {"zhihu": "知乎"}
        failed_ids = []

        news_data = convert_crawl_results_to_news_data(
            results, id_to_name, failed_ids, "12:00:00", "2026-01-02"
        )

        assert news_data.date == "2026-01-02"
        assert "zhihu" in news_data.items
        assert len(news_data.items["zhihu"]) == 1
        assert news_data.items["zhihu"][0].title == "测试标题"

    def test_convert_with_failed_sources(self):
        """测试转换包含失败来源的数据"""
        results = {}
        id_to_name = {"zhihu": "知乎"}
        failed_ids = ["zhihu"]

        news_data = convert_crawl_results_to_news_data(
            results, id_to_name, failed_ids, "12:00:00", "2026-01-02"
        )

        # 失败的来源不应该出现在结果中
        assert "zhihu" not in news_data.items


class TestStorageManagerEdgeCases:
    """StorageManager 边界情况测试"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def storage(self, temp_dir):
        """创建 StorageManager 实例"""
        return StorageManager(
            backend_type="local",
            data_dir=temp_dir,
            timezone="Asia/Shanghai"
        )

    def test_save_empty_news_data(self, storage):
        """测试保存空新闻数据"""
        from trendradar.storage.base import NewsData

        news_data = NewsData(date="2026-01-02", crawl_time="12:00", items={})
        storage.save_news_data(news_data)

        # 应该成功保存，但获取时返回 None
        retrieved_data = storage.get_today_all_data("2026-01-02")
        # 空数据的行为取决于实现，这里只测试不报错

    def test_backend_property(self, storage):
        """测试获取后端实例"""
        backend = storage.get_backend()
        assert backend is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
