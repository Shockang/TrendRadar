# coding=utf-8
"""
TrendRadar Storage Base 测试
测试数据模型和工具函数
"""

import pytest
from trendradar.storage.base import (
    NewsItem,
    RSSItem,
    RSSData,
    NewsData,
    convert_crawl_results_to_news_data,
    convert_news_data_to_results,
)


class TestNewsItem:
    """NewsItem 数据模型测试"""

    def test_to_dict(self):
        """测试转换为字典"""
        item = NewsItem(
            title="测试标题",
            source_id="zhihu",
            source_name="知乎",
            rank=1,
            url="http://example.com",
            mobile_url="http://m.example.com",
            crawl_time="10:00:00",
            ranks=[1, 2, 3],
            first_time="09:00:00",
            last_time="10:00:00",
            count=3,
        )

        data = item.to_dict()

        assert data["title"] == "测试标题"
        assert data["source_id"] == "zhihu"
        assert data["source_name"] == "知乎"
        assert data["rank"] == 1
        assert data["url"] == "http://example.com"
        assert data["mobile_url"] == "http://m.example.com"
        assert data["crawl_time"] == "10:00:00"
        assert data["ranks"] == [1, 2, 3]
        assert data["first_time"] == "09:00:00"
        assert data["last_time"] == "10:00:00"
        assert data["count"] == 3

    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            "title": "测试标题",
            "source_id": "zhihu",
            "source_name": "知乎",
            "rank": 1,
            "url": "http://example.com",
            "mobile_url": "http://m.example.com",
            "crawl_time": "10:00:00",
            "ranks": [1, 2, 3],
            "first_time": "09:00:00",
            "last_time": "10:00:00",
            "count": 3,
        }

        item = NewsItem.from_dict(data)

        assert item.title == "测试标题"
        assert item.source_id == "zhihu"
        assert item.source_name == "知乎"
        assert item.rank == 1
        assert item.url == "http://example.com"
        assert item.mobile_url == "http://m.example.com"
        assert item.crawl_time == "10:00:00"
        assert item.ranks == [1, 2, 3]
        assert item.first_time == "09:00:00"
        assert item.last_time == "10:00:00"
        assert item.count == 3

    def test_from_dict_with_defaults(self):
        """测试从字典创建 - 使用默认值"""
        data = {
            "title": "测试标题",
            "source_id": "zhihu",
        }

        item = NewsItem.from_dict(data)

        assert item.title == "测试标题"
        assert item.source_id == "zhihu"
        assert item.source_name == ""
        assert item.rank == 0
        assert item.url == ""
        assert item.mobile_url == ""
        assert item.crawl_time == ""
        assert item.ranks == []
        assert item.first_time == ""
        assert item.last_time == ""
        assert item.count == 1

    def test_roundtrip(self):
        """测试字典转换往返"""
        original = NewsItem(
            title="测试标题",
            source_id="zhihu",
            rank=1,
            url="http://example.com",
        )

        # 转换为字典再转换回来
        data = original.to_dict()
        restored = NewsItem.from_dict(data)

        assert restored.title == original.title
        assert restored.source_id == original.source_id
        assert restored.rank == original.rank
        assert restored.url == original.url


class TestRSSItem:
    """RSSItem 数据模型测试"""

    def test_to_dict(self):
        """测试转换为字典"""
        item = RSSItem(
            title="测试文章",
            feed_id="hacker-news",
            feed_name="Hacker News",
            url="http://example.com/article",
            published_at="2026-01-02T10:00:00Z",
            summary="这是一篇测试文章",
            author="测试作者",
            crawl_time="10:00:00",
            first_time="09:00:00",
            last_time="10:00:00",
            count=2,
        )

        data = item.to_dict()

        assert data["title"] == "测试文章"
        assert data["feed_id"] == "hacker-news"
        assert data["feed_name"] == "Hacker News"
        assert data["url"] == "http://example.com/article"
        assert data["published_at"] == "2026-01-02T10:00:00Z"
        assert data["summary"] == "这是一篇测试文章"
        assert data["author"] == "测试作者"
        assert data["crawl_time"] == "10:00:00"
        assert data["first_time"] == "09:00:00"
        assert data["last_time"] == "10:00:00"
        assert data["count"] == 2

    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            "title": "测试文章",
            "feed_id": "hacker-news",
            "feed_name": "Hacker News",
            "url": "http://example.com/article",
            "published_at": "2026-01-02T10:00:00Z",
            "summary": "这是一篇测试文章",
            "author": "测试作者",
            "crawl_time": "10:00:00",
            "first_time": "09:00:00",
            "last_time": "10:00:00",
            "count": 2,
        }

        item = RSSItem.from_dict(data)

        assert item.title == "测试文章"
        assert item.feed_id == "hacker-news"
        assert item.feed_name == "Hacker News"
        assert item.url == "http://example.com/article"
        assert item.published_at == "2026-01-02T10:00:00Z"
        assert item.summary == "这是一篇测试文章"
        assert item.author == "测试作者"
        assert item.crawl_time == "10:00:00"
        assert item.first_time == "09:00:00"
        assert item.last_time == "10:00:00"
        assert item.count == 2

    def test_from_dict_with_defaults(self):
        """测试从字典创建 - 使用默认值"""
        data = {
            "title": "测试文章",
            "feed_id": "hacker-news",
        }

        item = RSSItem.from_dict(data)

        assert item.title == "测试文章"
        assert item.feed_id == "hacker-news"
        assert item.feed_name == ""
        assert item.url == ""
        assert item.published_at == ""
        assert item.summary == ""
        assert item.author == ""
        assert item.crawl_time == ""
        assert item.first_time == ""
        assert item.last_time == ""
        assert item.count == 1


class TestRSSData:
    """RSSData 数据模型测试"""

    def test_to_dict(self):
        """测试转换为字典"""
        item1 = RSSItem(
            title="文章1",
            feed_id="hacker-news",
            url="http://example.com/1",
        )
        item2 = RSSItem(
            title="文章2",
            feed_id="hacker-news",
            url="http://example.com/2",
        )

        data = RSSData(
            date="2026-01-02",
            crawl_time="10:00:00",
            items={
                "hacker-news": [item1, item2]
            }
        )

        result = data.to_dict()

        assert result["date"] == "2026-01-02"
        assert result["crawl_time"] == "10:00:00"
        assert "hacker-news" in result["items"]
        assert len(result["items"]["hacker-news"]) == 2
        assert result["items"]["hacker-news"][0]["title"] == "文章1"
        assert result["items"]["hacker-news"][1]["title"] == "文章2"

    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            "date": "2026-01-02",
            "crawl_time": "10:00:00",
            "items": {
                "hacker-news": [
                    {
                        "title": "文章1",
                        "feed_id": "hacker-news",
                        "url": "http://example.com/1",
                    },
                    {
                        "title": "文章2",
                        "feed_id": "hacker-news",
                        "url": "http://example.com/2",
                    },
                ]
            }
        }

        rss_data = RSSData.from_dict(data)

        assert rss_data.date == "2026-01-02"
        assert rss_data.crawl_time == "10:00:00"
        assert "hacker-news" in rss_data.items
        assert len(rss_data.items["hacker-news"]) == 2
        assert rss_data.items["hacker-news"][0].title == "文章1"
        assert rss_data.items["hacker-news"][1].title == "文章2"


class TestNewsData:
    """NewsData 数据模型测试"""

    def test_to_dict(self):
        """测试转换为字典"""
        item1 = NewsItem(
            title="新闻1",
            source_id="zhihu",
            url="http://example.com/1",
        )
        item2 = NewsItem(
            title="新闻2",
            source_id="zhihu",
            url="http://example.com/2",
        )

        data = NewsData(
            date="2026-01-02",
            crawl_time="10:00:00",
            items={
                "zhihu": [item1, item2]
            }
        )

        result = data.to_dict()

        assert result["date"] == "2026-01-02"
        assert result["crawl_time"] == "10:00:00"
        assert "zhihu" in result["items"]
        assert len(result["items"]["zhihu"]) == 2
        assert result["items"]["zhihu"][0]["title"] == "新闻1"
        assert result["items"]["zhihu"][1]["title"] == "新闻2"

    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            "date": "2026-01-02",
            "crawl_time": "10:00:00",
            "items": {
                "zhihu": [
                    {
                        "title": "新闻1",
                        "source_id": "zhihu",
                        "url": "http://example.com/1",
                    },
                    {
                        "title": "新闻2",
                        "source_id": "zhihu",
                        "url": "http://example.com/2",
                    },
                ]
            }
        }

        news_data = NewsData.from_dict(data)

        assert news_data.date == "2026-01-02"
        assert news_data.crawl_time == "10:00:00"
        assert "zhihu" in news_data.items
        assert len(news_data.items["zhihu"]) == 2
        assert news_data.items["zhihu"][0].title == "新闻1"
        assert news_data.items["zhihu"][1].title == "新闻2"


class TestConvertCrawlResultsToNewsData:
    """convert_crawl_results_to_news_data 函数测试"""

    def test_basic_conversion(self):
        """测试基本转换"""
        results = {
            "zhihu": {
                "测试标题1": {
                    "time": "10:00:00",
                    "ranks": [1],
                    "url": "http://example.com/1",
                    "mobileUrl": "http://m.example.com/1",
                },
                "测试标题2": {
                    "time": "10:00:00",
                    "ranks": [2],
                    "url": "http://example.com/2",
                    "mobileUrl": "",
                },
            }
        }
        id_to_name = {"zhihu": "知乎"}
        failed_ids = []
        crawl_time = "10:00:00"
        crawl_date = "2026-01-02"

        news_data = convert_crawl_results_to_news_data(
            results, id_to_name, failed_ids, crawl_time, crawl_date
        )

        assert news_data.date == crawl_date
        assert news_data.crawl_time == crawl_time
        assert "zhihu" in news_data.items
        assert len(news_data.items["zhihu"]) == 2
        assert news_data.items["zhihu"][0].title == "测试标题1"
        assert news_data.items["zhihu"][1].title == "测试标题2"
        assert news_data.items["zhihu"][0].source_name == "知乎"

    def test_with_failed_ids(self):
        """测试包含失败的ID"""
        results = {
            "zhihu": {
                "测试标题": {
                    "time": "10:00:00",
                    "ranks": [1],
                    "url": "http://example.com",
                    "mobileUrl": "",
                },
            }
        }
        id_to_name = {"zhihu": "知乎"}
        failed_ids = ["weibo"]
        crawl_time = "10:00:00"
        crawl_date = "2026-01-02"

        news_data = convert_crawl_results_to_news_data(
            results, id_to_name, failed_ids, crawl_time, crawl_date
        )

        # 应该包含失败的平台，但items为空
        assert "zhihu" in news_data.items
        assert len(news_data.items["zhihu"]) == 1

    def test_empty_results(self):
        """测试空结果"""
        results = {}
        id_to_name = {}
        failed_ids = []
        crawl_time = "10:00:00"
        crawl_date = "2026-01-02"

        news_data = convert_crawl_results_to_news_data(
            results, id_to_name, failed_ids, crawl_time, crawl_date
        )

        assert news_data.date == crawl_date
        assert news_data.crawl_time == crawl_time
        assert len(news_data.items) == 0


class TestConvertNewsDataToResults:
    """convert_news_data_to_results 函数测试"""

    def test_basic_conversion(self):
        """测试基本转换"""
        items = {
            "zhihu": [
                NewsItem(
                    title="测试标题",
                    source_id="zhihu",
                    source_name="知乎",
                    rank=1,
                    url="http://example.com",
                    crawl_time="10:00:00",
                    ranks=[1],
                    first_time="10:00:00",
                    last_time="10:00:00",
                    count=1,
                )
            ]
        }

        news_data = NewsData(
            date="2026-01-02",
            crawl_time="10:00:00",
            items=items,
            id_to_name={"zhihu": "知乎"}
        )

        results, id_to_name, title_info = convert_news_data_to_results(news_data)

        assert "zhihu" in results
        assert "测试标题" in results["zhihu"]
        assert results["zhihu"]["测试标题"]["ranks"] == [1]
        assert results["zhihu"]["测试标题"]["url"] == "http://example.com"
        assert id_to_name["zhihu"] == "知乎"
        assert "zhihu" in title_info
        assert "测试标题" in title_info["zhihu"]
        assert title_info["zhihu"]["测试标题"]["count"] == 1

    def test_empty_data(self):
        """测试空数据"""
        news_data = NewsData(
            date="2026-01-02",
            crawl_time="10:00:00",
            items={}
        )

        results, id_to_name, title_info = convert_news_data_to_results(news_data)

        assert len(results) == 0
        assert len(id_to_name) == 0
        assert len(title_info) == 0

    def test_multiple_sources(self):
        """测试多个数据源"""
        items = {
            "zhihu": [
                NewsItem(
                    title="知乎热榜",
                    source_id="zhihu",
                    source_name="知乎",
                    rank=1,
                    url="http://zhihu.com",
                    crawl_time="10:00:00",
                )
            ],
            "weibo": [
                NewsItem(
                    title="微博热榜",
                    source_id="weibo",
                    source_name="微博",
                    rank=1,
                    url="http://weibo.com",
                    crawl_time="10:00:00",
                )
            ]
        }

        news_data = NewsData(
            date="2026-01-02",
            crawl_time="10:00:00",
            items=items,
            id_to_name={"zhihu": "知乎", "weibo": "微博"}
        )

        results, id_to_name, title_info = convert_news_data_to_results(news_data)

        assert len(results) == 2
        assert "zhihu" in results
        assert "weibo" in results
        assert id_to_name["zhihu"] == "知乎"
        assert id_to_name["weibo"] == "微博"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
