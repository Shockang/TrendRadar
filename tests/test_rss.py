# coding=utf-8
"""
RSS 模块测试
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from requests.exceptions import Timeout, RequestException

from trendradar.crawler.rss.fetcher import RSSFetcher, RSSFeedConfig
from trendradar.crawler.rss.parser import RSSParser, ParsedRSSItem
from trendradar.storage.base import RSSItem, RSSData


class TestRSSParser:
    """RSS 解析器测试"""

    def test_init_requires_feedparser(self):
        """测试初始化需要 feedparser"""
        with patch('trendradar.crawler.rss.parser.HAS_FEEDPARSER', False):
            with pytest.raises(ImportError, match="feedparser"):
                RSSParser()

    def test_init_with_custom_max_summary_length(self):
        """测试自定义摘要长度"""
        parser = RSSParser(max_summary_length=200)
        assert parser.max_summary_length == 200

    def test_clean_text_basic(self):
        """测试基本文本清理"""
        parser = RSSParser()
        text = "  Hello   World  "
        result = parser._clean_text(text)
        assert result == "Hello World"

    def test_clean_text_with_html_entities(self):
        """测试 HTML 实体解码"""
        parser = RSSParser()
        text = "Hello &amp; World"
        result = parser._clean_text(text)
        assert result == "Hello & World"

    def test_clean_text_with_html_tags(self):
        """测试 HTML 标签移除"""
        parser = RSSParser()
        text = "<p>Hello <b>World</b></p>"
        result = parser._clean_text(text)
        assert result == "Hello World"

    def test_clean_text_empty_string(self):
        """测试空字符串"""
        parser = RSSParser()
        assert parser._clean_text("") == ""
        assert parser._clean_text(None) == ""  # type: ignore

    def test_parse_iso_date_valid(self):
        """测试有效 ISO 日期解析"""
        parser = RSSParser()
        result = parser._parse_iso_date("2025-01-02T12:00:00Z")
        assert result is not None
        assert "2025-01-02" in result

    def test_parse_iso_date_invalid(self):
        """测试无效 ISO 日期解析"""
        parser = RSSParser()
        result = parser._parse_iso_date("invalid-date")
        assert result is None

    def test_parse_iso_date_empty(self):
        """测试空日期"""
        parser = RSSParser()
        assert parser._parse_iso_date("") is None
        assert parser._parse_iso_date(None) is None  # type: ignore

    def test_is_json_feed_true(self):
        """测试 JSON Feed 检测（真）"""
        parser = RSSParser()
        content = json.dumps({
            "version": "https://jsonfeed.org/version/1.1",
            "title": "Test Feed"
        })
        assert parser._is_json_feed(content) is True

    def test_is_json_feed_false(self):
        """测试 JSON Feed 检测（假）"""
        parser = RSSParser()
        # RSS XML
        assert parser._is_json_feed('<?xml version="1.0"?><rss></rss>') is False
        # Plain JSON
        assert parser._is_json_feed('{"title": "test"}') is False
        # Invalid JSON
        assert parser._is_json_feed('{invalid json}') is False

    def test_parse_json_feed_item_basic(self):
        """测试解析基本 JSON Feed 条目"""
        parser = RSSParser()
        item_data = {
            "id": "1",
            "title": "Test Article",
            "url": "https://example.com/article",
            "date_published": "2025-01-02T12:00:00Z",
            "summary": "Test summary",
            "authors": [{"name": "John Doe"}]
        }
        result = parser._parse_json_feed_item(item_data)
        assert result is not None
        assert result.title == "Test Article"
        assert result.url == "https://example.com/article"
        assert result.summary == "Test summary"
        assert result.author == "John Doe"

    def test_parse_json_feed_item_without_title(self):
        """测试无标题的 JSON Feed 条目"""
        parser = RSSParser()
        item_data = {
            "id": "1",
            "url": "https://example.com/article",
            "content_text": "This is a long content that should be used as title when title is missing"
        }
        result = parser._parse_json_feed_item(item_data)
        assert result is not None
        assert "This is a long content" in result.title

    def test_parse_json_feed_item_long_summary(self):
        """测试长摘要截断"""
        parser = RSSParser(max_summary_length=50)
        item_data = {
            "id": "1",
            "title": "Test",
            "url": "https://example.com",
            "summary": "x" * 200
        }
        result = parser._parse_json_feed_item(item_data)
        assert result is not None
        assert len(result.summary) <= 53  # 50 + "..."

    def test_parse_json_feed_item_multiple_authors(self):
        """测试多个作者"""
        parser = RSSParser()
        item_data = {
            "id": "1",
            "title": "Test",
            "url": "https://example.com",
            "authors": [
                {"name": "Alice"},
                {"name": "Bob"}
            ]
        }
        result = parser._parse_json_feed_item(item_data)
        assert result is not None
        assert result.author == "Alice, Bob"

    def test_parse_json_feed_item_invalid(self):
        """测试无效 JSON Feed 条目"""
        parser = RSSParser()
        # 无标题且无内容
        result = parser._parse_json_feed_item({"id": "1"})
        assert result is None

    def test_parse_author_basic(self):
        """测试基本作者解析"""
        parser = RSSParser()
        entry = {"author": "John Doe"}
        result = parser._parse_author(entry)
        assert result == "John Doe"

    def test_parse_author_from_dc_creator(self):
        """测试从 dc:creator 解析作者"""
        parser = RSSParser()
        entry = {"dc_creator": "Jane Doe"}
        result = parser._parse_author(entry)
        assert result == "Jane Doe"

    def test_parse_author_from_list(self):
        """测试从 authors 列表解析"""
        parser = RSSParser()
        entry = {"authors": [{"name": "Alice"}, {"name": "Bob"}]}
        result = parser._parse_author(entry)
        assert result == "Alice, Bob"

    def test_parse_author_none(self):
        """测试无作者"""
        parser = RSSParser()
        entry = {}
        result = parser._parse_author(entry)
        assert result is None

    def test_parse_summary_basic(self):
        """测试基本摘要解析"""
        parser = RSSParser()
        entry = {"summary": "Test summary"}
        result = parser._parse_summary(entry)
        assert result == "Test summary"

    def test_parse_summary_from_description(self):
        """测试从 description 解析摘要"""
        parser = RSSParser()
        entry = {"description": "Test description"}
        result = parser._parse_summary(entry)
        assert result == "Test description"

    def test_parse_summary_from_content(self):
        """测试从 content 解析摘要"""
        parser = RSSParser()
        entry = {"content": [{"value": "Test content"}]}
        result = parser._parse_summary(entry)
        assert result == "Test content"

    def test_parse_summary_truncate(self):
        """测试摘要截断"""
        parser = RSSParser(max_summary_length=50)
        entry = {"summary": "x" * 200}
        result = parser._parse_summary(entry)
        assert len(result) <= 53  # 50 + "..."

    def test_parse_summary_none(self):
        """测试无摘要"""
        parser = RSSParser()
        entry = {}
        result = parser._parse_summary(entry)
        assert result is None

    def test_parse_entry_basic(self, mock_feedparser_entry):
        """测试基本条目解析"""
        parser = RSSParser()
        result = parser._parse_entry(mock_feedparser_entry)
        assert result is not None
        assert result.title == "Test Title"
        assert result.url == "https://example.com/article"

    def test_parse_entry_without_title(self):
        """测试无标题条目"""
        parser = RSSParser()
        entry = {"link": "https://example.com"}
        result = parser._parse_entry(entry)
        assert result is None

    def test_parse_date_from_published_parsed(self):
        """测试从 published_parsed 解析日期"""
        parser = RSSParser()
        dt = datetime(2025, 1, 2, 12, 0, 0)
        entry = {"published_parsed": dt.timetuple()}
        result = parser._parse_date(entry)
        assert result is not None
        assert "2025-01-02" in result

    def test_parse_date_from_published_string(self):
        """测试从 published 字符串解析日期"""
        parser = RSSParser()
        entry = {"published": "Wed, 02 Jan 2025 12:00:00 GMT"}
        result = parser._parse_date(entry)
        assert result is not None
        assert "2025-01-02" in result

    def test_parse_date_from_iso_string(self):
        """测试从 ISO 字符串解析日期"""
        parser = RSSParser()
        entry = {"published": "2025-01-02T12:00:00Z"}
        result = parser._parse_date(entry)
        assert result is not None
        assert "2025-01-02" in result

    def test_parse_date_none(self):
        """测试无日期"""
        parser = RSSParser()
        entry = {}
        result = parser._parse_date(entry)
        assert result is None

    def test_parse_rss_feed(self):
        """测试解析 RSS Feed"""
        parser = RSSParser()
        with patch('trendradar.crawler.rss.parser.feedparser') as mock_fp:
            # Mock entries with proper string values
            mock_entry1 = MagicMock()
            mock_entry1.get = lambda key, default=None: {
                "title": "Article 1",
                "link": "https://example.com/1",
                "summary": "Summary 1"
            }.get(key, default)
            mock_entry1.get.return_value = "Article 1" if mock_entry1.get("title") == "title" else mock_entry1.get("title")

            mock_entry2 = MagicMock()
            mock_entry2.get = lambda key, default=None: {
                "title": "Article 2",
                "link": "https://example.com/2",
                "summary": "Summary 2"
            }.get(key, default)

            mock_fp.parse.return_value = MagicMock(
                bozo=False,
                entries=[mock_entry1, mock_entry2]
            )

            results = parser.parse('<?xml version="1.0"?><rss></rss>', "https://example.com/feed")
            assert len(results) == 2
            assert results[0].title == "Article 1"
            assert results[1].title == "Article 2"

    def test_parse_json_feed(self):
        """测试解析 JSON Feed"""
        parser = RSSParser()
        content = json.dumps({
            "version": "https://jsonfeed.org/version/1.1",
            "title": "Test Feed",
            "items": [
                {
                    "id": "1",
                    "title": "Article 1",
                    "url": "https://example.com/1",
                    "date_published": "2025-01-02T12:00:00Z",
                    "summary": "Summary 1"
                },
                {
                    "id": "2",
                    "title": "Article 2",
                    "url": "https://example.com/2"
                }
            ]
        })
        results = parser.parse(content, "https://example.com/feed")
        assert len(results) == 2
        assert results[0].title == "Article 1"
        assert results[1].title == "Article 2"

    def test_parse_invalid_json_feed(self):
        """测试解析无效 JSON Feed"""
        parser = RSSParser()
        content = json.dumps({
            "version": "https://jsonfeed.org/version/1.1",
            "title": "Test Feed"
        })
        with pytest.raises(ValueError, match="JSON Feed 解析失败"):
            parser._parse_json_feed("{invalid json}", "https://example.com")

    def test_parse_empty_json_feed(self):
        """测试解析空 JSON Feed"""
        parser = RSSParser()
        content = json.dumps({
            "version": "https://jsonfeed.org/version/1.1",
            "title": "Test Feed",
            "items": []
        })
        results = parser._parse_json_feed(content, "https://example.com")
        assert len(results) == 0


class TestRSSFetcher:
    """RSS 抓取器测试"""

    def test_init_basic(self):
        """测试基本初始化"""
        feeds = [
            RSSFeedConfig(
                id="test",
                name="Test Feed",
                url="https://example.com/feed"
            )
        ]
        fetcher = RSSFetcher(feeds=feeds)
        assert len(fetcher.feeds) == 1
        assert fetcher.request_interval == 2000
        assert fetcher.timeout == 15
        assert fetcher.use_proxy is False

    def test_init_filters_disabled_feeds(self):
        """测试初始化时过滤禁用的 feed"""
        feeds = [
            RSSFeedConfig(id="test1", name="Test 1", url="https://example.com/1", enabled=True),
            RSSFeedConfig(id="test2", name="Test 2", url="https://example.com/2", enabled=False),
        ]
        fetcher = RSSFetcher(feeds=feeds)
        assert len(fetcher.feeds) == 1
        assert fetcher.feeds[0].id == "test1"

    def test_init_with_proxy(self):
        """测试使用代理初始化"""
        feeds = [RSSFeedConfig(id="test", name="Test", url="https://example.com/feed")]
        fetcher = RSSFetcher(
            feeds=feeds,
            use_proxy=True,
            proxy_url="http://proxy.example.com:8080"
        )
        assert fetcher.use_proxy is True
        assert fetcher.proxy_url == "http://proxy.example.com:8080"
        # 验证 session 配置了代理
        assert fetcher.session.proxies == {
            "http": "http://proxy.example.com:8080",
            "https": "http://proxy.example.com:8080",
        }

    def test_create_session_headers(self):
        """测试 session 创建时设置正确的 headers"""
        feeds = [RSSFeedConfig(id="test", name="Test", url="https://example.com/feed")]
        fetcher = RSSFetcher(feeds=feeds)
        assert "User-Agent" in fetcher.session.headers
        assert "Accept" in fetcher.session.headers
        assert "feed+json" in fetcher.session.headers["Accept"]

    def test_filter_by_freshness_disabled(self):
        """测试禁用新鲜度过滤"""
        feeds = [RSSFeedConfig(id="test", name="Test", url="https://example.com/feed")]
        fetcher = RSSFetcher(feeds=feeds, freshness_enabled=False)

        items = [
            RSSItem(title="Old", feed_id="test", url="https://example.com/old",
                   published_at="2020-01-01T00:00:00", crawl_time="12:00",
                   first_time="12:00", last_time="12:00", count=1)
        ]
        filtered, count = fetcher._filter_by_freshness(items, feeds[0])
        assert len(filtered) == 1
        assert count == 0

    def test_filter_by_freshness_within_days(self):
        """测试新鲜度过滤（在指定天数内）"""
        feeds = [RSSFeedConfig(id="test", name="Test", url="https://example.com/feed")]
        fetcher = RSSFetcher(feeds=feeds, freshness_enabled=True, default_max_age_days=3)

        now = datetime.now()
        recent_date = (now - timedelta(days=1)).isoformat()

        items = [
            RSSItem(title="Recent", feed_id="test", url="https://example.com/recent",
                   published_at=recent_date, crawl_time="12:00",
                   first_time="12:00", last_time="12:00", count=1)
        ]
        filtered, count = fetcher._filter_by_freshness(items, feeds[0])
        assert len(filtered) == 1
        assert count == 0

    def test_filter_by_freshness_old_item(self):
        """测试新鲜度过滤（旧文章）"""
        feeds = [RSSFeedConfig(id="test", name="Test", url="https://example.com/feed")]
        fetcher = RSSFetcher(feeds=feeds, freshness_enabled=True, default_max_age_days=3)

        items = [
            RSSItem(title="Old", feed_id="test", url="https://example.com/old",
                   published_at="2020-01-01T00:00:00", crawl_time="12:00",
                   first_time="12:00", last_time="12:00", count=1)
        ]
        filtered, count = fetcher._filter_by_freshness(items, feeds[0])
        assert len(filtered) == 0
        assert count == 1

    def test_filter_by_freshness_no_date(self):
        """测试无发布日期的文章（保留）"""
        feeds = [RSSFeedConfig(id="test", name="Test", url="https://example.com/feed")]
        fetcher = RSSFetcher(feeds=feeds, freshness_enabled=True, default_max_age_days=3)

        items = [
            RSSItem(title="No Date", feed_id="test", url="https://example.com/nodate",
                   published_at="", crawl_time="12:00",
                   first_time="12:00", last_time="12:00", count=1)
        ]
        filtered, count = fetcher._filter_by_freshness(items, feeds[0])
        assert len(filtered) == 1
        assert count == 0

    def test_filter_by_freshness_feed_override(self):
        """测试 feed 覆盖全局 max_age_days"""
        feeds = [
            RSSFeedConfig(id="test", name="Test", url="https://example.com/feed",
                         max_age_days=7)  # 覆盖全局的 3 天
        ]
        fetcher = RSSFetcher(feeds=feeds, freshness_enabled=True, default_max_age_days=3)

        now = datetime.now()
        date_5_days_ago = (now - timedelta(days=5)).isoformat()

        items = [
            RSSItem(title="5 days ago", feed_id="test", url="https://example.com/old",
                   published_at=date_5_days_ago, crawl_time="12:00",
                   first_time="12:00", last_time="12:00", count=1)
        ]
        # 全局设置会过滤掉，但 feed 覆盖为 7 天后应该保留
        filtered, count = fetcher._filter_by_freshness(items, feeds[0])
        assert len(filtered) == 1
        assert count == 0

    def test_filter_by_freshness_feed_disabled(self):
        """测试 feed 禁用新鲜度过滤（max_age_days=0）"""
        feeds = [
            RSSFeedConfig(id="test", name="Test", url="https://example.com/feed",
                         max_age_days=0)  # 禁用过滤
        ]
        fetcher = RSSFetcher(feeds=feeds, freshness_enabled=True, default_max_age_days=3)

        items = [
            RSSItem(title="Old", feed_id="test", url="https://example.com/old",
                   published_at="2020-01-01T00:00:00", crawl_time="12:00",
                   first_time="12:00", last_time="12:00", count=1)
        ]
        # 即使全局启用，feed 设置为 0 后不过滤
        filtered, count = fetcher._filter_by_freshness(items, feeds[0])
        assert len(filtered) == 1
        assert count == 0

    @patch('trendradar.crawler.rss.fetcher.requests.Session.get')
    def test_fetch_feed_success(self, mock_get):
        """测试成功抓取 feed"""
        feeds = [RSSFeedConfig(id="test", name="Test Feed", url="https://example.com/feed")]
        fetcher = RSSFetcher(feeds=feeds)

        mock_response = Mock()
        mock_response.text = '<?xml version="1.0"?><rss version="2.0"><channel><item><title>Test Article</title><link>https://example.com/article</link></item></channel></rss>'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        with patch.object(fetcher.parser, 'parse', return_value=[
            ParsedRSSItem(title="Test Article", url="https://example.com/article")
        ]):
            items, error = fetcher.fetch_feed(feeds[0])
            assert len(items) == 1
            assert error is None
            assert items[0].title == "Test Article"

    @patch('trendradar.crawler.rss.fetcher.requests.Session.get')
    def test_fetch_feed_timeout(self, mock_get):
        """测试抓取超时"""
        feeds = [RSSFeedConfig(id="test", name="Test Feed", url="https://example.com/feed")]
        fetcher = RSSFetcher(feeds=feeds, timeout=5)

        mock_get.side_effect = Timeout("Connection timeout")

        items, error = fetcher.fetch_feed(feeds[0])
        assert len(items) == 0
        assert error is not None
        assert "超时" in error

    @patch('trendradar.crawler.rss.fetcher.requests.Session.get')
    def test_fetch_feed_request_error(self, mock_get):
        """测试请求错误"""
        feeds = [RSSFeedConfig(id="test", name="Test Feed", url="https://example.com/feed")]
        fetcher = RSSFetcher(feeds=feeds)

        mock_get.side_effect = RequestException("Connection error")

        items, error = fetcher.fetch_feed(feeds[0])
        assert len(items) == 0
        assert error is not None
        assert "请求失败" in error

    @patch('trendradar.crawler.rss.fetcher.requests.Session.get')
    def test_fetch_feed_max_items(self, mock_get):
        """测试限制最大条目数"""
        feeds = [
            RSSFeedConfig(id="test", name="Test Feed", url="https://example.com/feed",
                         max_items=2)
        ]
        fetcher = RSSFetcher(feeds=feeds)

        mock_response = Mock()
        mock_response.text = "content"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # 模拟解析返回 5 个条目
        with patch.object(fetcher.parser, 'parse', return_value=[
            ParsedRSSItem(title=f"Article {i}", url=f"https://example.com/{i}")
            for i in range(5)
        ]):
            items, error = fetcher.fetch_feed(feeds[0])
            assert len(items) == 2  # 应该只返回 2 个
            assert error is None

    @patch('trendradar.crawler.rss.fetcher.time.sleep')
    @patch('trendradar.crawler.rss.fetcher.RSSFetcher.fetch_feed')
    def test_fetch_all_success(self, mock_fetch_feed, mock_sleep):
        """测试抓取所有 feed（成功）"""
        feeds = [
            RSSFeedConfig(id="feed1", name="Feed 1", url="https://example.com/feed1"),
            RSSFeedConfig(id="feed2", name="Feed 2", url="https://example.com/feed2"),
        ]
        fetcher = RSSFetcher(feeds=feeds)

        mock_fetch_feed.side_effect = [
            ([RSSItem(title="Item 1", feed_id="feed1", url="https://example.com/1",
                     crawl_time="12:00", first_time="12:00", last_time="12:00", count=1)], None),
            ([RSSItem(title="Item 2", feed_id="feed2", url="https://example.com/2",
                     crawl_time="12:00", first_time="12:00", last_time="12:00", count=1)], None),
        ]

        result = fetcher.fetch_all()

        assert len(result.items) == 2
        assert len(result.failed_ids) == 0
        assert result.id_to_name["feed1"] == "Feed 1"
        assert result.id_to_name["feed2"] == "Feed 2"
        assert len(result.items["feed1"]) == 1
        assert len(result.items["feed2"]) == 1

    @patch('trendradar.crawler.rss.fetcher.time.sleep')
    @patch('trendradar.crawler.rss.fetcher.RSSFetcher.fetch_feed')
    def test_fetch_all_with_failure(self, mock_fetch_feed, mock_sleep):
        """测试抓取所有 feed（部分失败）"""
        feeds = [
            RSSFeedConfig(id="feed1", name="Feed 1", url="https://example.com/feed1"),
            RSSFeedConfig(id="feed2", name="Feed 2", url="https://example.com/feed2"),
        ]
        fetcher = RSSFetcher(feeds=feeds)

        mock_fetch_feed.side_effect = [
            ([RSSItem(title="Item 1", feed_id="feed1", url="https://example.com/1",
                     crawl_time="12:00", first_time="12:00", last_time="12:00", count=1)], None),
            ([], "Connection failed"),
        ]

        result = fetcher.fetch_all()

        assert len(result.items) == 1  # 只有 feed1 成功
        assert len(result.failed_ids) == 1
        assert "feed2" in result.failed_ids

    def test_from_config_basic(self):
        """测试从配置创建"""
        config = {
            "enabled": True,
            "request_interval": 3000,
            "timeout": 20,
            "freshness_filter": {
                "enabled": True,
                "max_age_days": 5
            },
            "feeds": [
                {
                    "id": "test",
                    "name": "Test Feed",
                    "url": "https://example.com/feed",
                    "max_items": 10,
                    "enabled": True
                }
            ]
        }
        fetcher = RSSFetcher.from_config(config)
        assert len(fetcher.feeds) == 1
        assert fetcher.request_interval == 3000
        assert fetcher.timeout == 20
        assert fetcher.default_max_age_days == 5
        assert fetcher.freshness_enabled is True

    def test_from_config_with_max_age_days(self):
        """测试从配置创建（带 max_age_days）"""
        config = {
            "enabled": True,
            "freshness_filter": {
                "enabled": True,
                "max_age_days": 3
            },
            "feeds": [
                {
                    "id": "test1",
                    "name": "Feed 1",
                    "url": "https://example.com/feed1",
                    "max_age_days": 7
                },
                {
                    "id": "test2",
                    "name": "Feed 2",
                    "url": "https://example.com/feed2",
                    "max_age_days": 0
                }
            ]
        }
        fetcher = RSSFetcher.from_config(config)
        assert fetcher.feeds[0].max_age_days == 7
        assert fetcher.feeds[1].max_age_days == 0

    def test_from_config_invalid_max_age_days(self):
        """测试从配置创建（无效 max_age_days）"""
        config = {
            "enabled": True,
            "freshness_filter": {"enabled": True, "max_age_days": 3},
            "feeds": [
                {
                    "id": "test",
                    "name": "Test",
                    "url": "https://example.com/feed",
                    "max_age_days": -1
                }
            ]
        }
        fetcher = RSSFetcher.from_config(config)
        # 负数应该被忽略，使用全局默认值
        assert fetcher.feeds[0].max_age_days is None

    def test_from_config_missing_required_fields(self):
        """测试从配置创建（缺少必需字段）"""
        config = {
            "enabled": True,
            "feeds": [
                {"name": "Test"}  # 缺少 id 和 url
            ]
        }
        fetcher = RSSFetcher.from_config(config)
        # 应该跳过无效的 feed
        assert len(fetcher.feeds) == 0


class TestRSSFeedConfig:
    """RSS Feed 配置测试"""

    def test_create_basic(self):
        """测试创建基本配置"""
        config = RSSFeedConfig(
            id="test",
            name="Test Feed",
            url="https://example.com/feed"
        )
        assert config.id == "test"
        assert config.name == "Test Feed"
        assert config.url == "https://example.com/feed"
        assert config.max_items == 0
        assert config.enabled is True

    def test_create_with_options(self):
        """测试创建带选项的配置"""
        config = RSSFeedConfig(
            id="test",
            name="Test Feed",
            url="https://example.com/feed",
            max_items=10,
            enabled=False,
            max_age_days=7
        )
        assert config.max_items == 10
        assert config.enabled is False
        assert config.max_age_days == 7


# ===== Fixtures =====

@pytest.fixture
def mock_feedparser_entry():
    """创建 mock feedparser entry"""
    return {
        "title": "Test Title",
        "link": "https://example.com/article",
        "published_parsed": datetime(2025, 1, 2, 12, 0, 0).timetuple(),
        "summary": "Test Summary",
        "author": "Test Author"
    }


@pytest.fixture
def sample_rss_content():
    """示例 RSS 内容"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <title>Test Feed</title>
            <item>
                <title>Article 1</title>
                <link>https://example.com/1</link>
                <pubDate>Wed, 02 Jan 2025 12:00:00 GMT</pubDate>
                <description>Summary 1</description>
            </item>
        </channel>
    </rss>'''
