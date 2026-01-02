# coding=utf-8
"""
DataFetcher 测试用例
"""

import json
from unittest.mock import Mock, patch, MagicMock
import pytest
import requests

from trendradar.crawler.fetcher import DataFetcher


class TestDataFetcher:
    """DataFetcher 单元测试"""

    def test_init_with_defaults(self):
        """测试默认初始化"""
        fetcher = DataFetcher()
        assert fetcher.api_url == DataFetcher.DEFAULT_API_URL
        assert fetcher.proxy_url is None

    def test_init_with_proxy(self):
        """测试使用代理初始化"""
        proxy_url = "http://proxy.example.com:8080"
        fetcher = DataFetcher(proxy_url=proxy_url)
        assert fetcher.proxy_url == proxy_url
        assert fetcher.api_url == DataFetcher.DEFAULT_API_URL

    def test_init_with_custom_api_url(self):
        """测试自定义 API URL 初始化"""
        custom_url = "https://custom.api.com/api"
        fetcher = DataFetcher(api_url=custom_url)
        assert fetcher.api_url == custom_url
        assert fetcher.proxy_url is None

    def test_init_with_both_params(self):
        """测试同时设置代理和 API URL"""
        proxy_url = "http://proxy.example.com:8080"
        custom_url = "https://custom.api.com/api"
        fetcher = DataFetcher(proxy_url=proxy_url, api_url=custom_url)
        assert fetcher.proxy_url == proxy_url
        assert fetcher.api_url == custom_url

    @patch('trendradar.crawler.fetcher.requests.get')
    def test_fetch_data_success(self, mock_get):
        """测试成功获取数据"""
        # Mock 响应
        mock_response = Mock()
        mock_response.text = '{"status": "success", "items": []}'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        fetcher = DataFetcher()
        data, id_value, alias = fetcher.fetch_data("test_id")

        assert data is not None
        assert id_value == "test_id"
        assert alias == "test_id"
        mock_get.assert_called_once()

    @patch('trendradar.crawler.fetcher.requests.get')
    def test_fetch_data_with_tuple(self, mock_get):
        """测试使用元组形式的 ID"""
        mock_response = Mock()
        mock_response.text = '{"status": "success", "items": []}'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        fetcher = DataFetcher()
        data, id_value, alias = fetcher.fetch_data(("test_id", "custom_alias"))

        assert data is not None
        assert id_value == "test_id"
        assert alias == "custom_alias"

    @patch('trendradar.crawler.fetcher.requests.get')
    def test_fetch_data_cache_status(self, mock_get):
        """测试缓存状态响应"""
        mock_response = Mock()
        mock_response.text = '{"status": "cache", "items": []}'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        fetcher = DataFetcher()
        data, id_value, alias = fetcher.fetch_data("test_id")

        assert data is not None
        assert id_value == "test_id"

    @patch('trendradar.crawler.fetcher.requests.get')
    def test_fetch_data_with_proxy(self, mock_get):
        """测试使用代理获取数据"""
        mock_response = Mock()
        mock_response.text = '{"status": "success", "items": []}'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        proxy_url = "http://proxy.example.com:8080"
        fetcher = DataFetcher(proxy_url=proxy_url)
        fetcher.fetch_data("test_id")

        # 验证代理设置被传递
        call_args = mock_get.call_args
        assert 'proxies' in call_args.kwargs
        assert call_args.kwargs['proxies']['http'] == proxy_url
        assert call_args.kwargs['proxies']['https'] == proxy_url

    @patch('trendradar.crawler.fetcher.requests.get')
    def test_fetch_data_invalid_status(self, mock_get):
        """测试无效状态响应"""
        mock_response = Mock()
        mock_response.text = '{"status": "error", "items": []}'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        fetcher = DataFetcher()
        data, id_value, alias = fetcher.fetch_data("test_id", max_retries=0)

        # 第一次请求失败后，应该返回 None
        assert data is None
        assert id_value == "test_id"

    @patch('trendradar.crawler.fetcher.requests.get')
    @patch('trendradar.crawler.fetcher.time.sleep')
    def test_fetch_data_retry_on_failure(self, mock_sleep, mock_get):
        """测试失败重试机制"""
        # 前两次失败，第三次成功
        mock_response_fail = Mock()
        mock_response_fail.raise_for_status.side_effect = requests.RequestException("Network error")

        mock_response_success = Mock()
        mock_response_success.text = '{"status": "success", "items": []}'
        mock_response_success.raise_for_status = Mock()

        mock_get.side_effect = [
            mock_response_fail,
            mock_response_fail,
            mock_response_success
        ]

        fetcher = DataFetcher()
        data, id_value, alias = fetcher.fetch_data("test_id", max_retries=2)

        assert data is not None
        assert mock_get.call_count == 3
        assert mock_sleep.call_count == 2

    @patch('trendradar.crawler.fetcher.requests.get')
    def test_fetch_data_max_retries_exceeded(self, mock_get):
        """测试超过最大重试次数"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.RequestException("Network error")
        mock_get.return_value = mock_response

        fetcher = DataFetcher()
        data, id_value, alias = fetcher.fetch_data("test_id", max_retries=1)

        assert data is None
        # 初始请求 + 1次重试 = 2次
        assert mock_get.call_count == 2

    @patch('trendradar.crawler.fetcher.requests.get')
    def test_crawl_websites_single_id(self, mock_get):
        """测试爬取单个网站"""
        mock_response = Mock()
        mock_response.text = json.dumps({
            "status": "success",
            "items": [
                {"title": "Test News 1", "url": "http://example.com/1", "mobileUrl": "http://m.example.com/1"},
                {"title": "Test News 2", "url": "http://example.com/2", "mobileUrl": "http://m.example.com/2"},
            ]
        })
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        fetcher = DataFetcher()
        results, id_to_name, failed_ids = fetcher.crawl_websites(["test_id"])

        assert "test_id" in results
        assert len(results["test_id"]) == 2
        assert "Test News 1" in results["test_id"]
        assert "Test News 2" in results["test_id"]
        assert id_to_name["test_id"] == "test_id"
        assert len(failed_ids) == 0

    @patch('trendradar.crawler.fetcher.requests.get')
    def test_crawl_websites_multiple_ids(self, mock_get):
        """测试爬取多个网站"""
        def create_response(title_prefix):
            return Mock(
                text=json.dumps({
                    "status": "success",
                    "items": [
                        {"title": f"{title_prefix} News 1", "url": f"http://example.com/{title_prefix}1"},
                        {"title": f"{title_prefix} News 2", "url": f"http://example.com/{title_prefix}2"},
                    ]
                }),
                raise_for_status=Mock()
            )

        mock_get.side_effect = [
            create_response("Source1"),
            create_response("Source2"),
        ]

        fetcher = DataFetcher()
        results, id_to_name, failed_ids = fetcher.crawl_websites(
            ["source1", "source2"],
            request_interval=0  # 不等待
        )

        assert len(results) == 2
        assert "source1" in results
        assert "source2" in results
        assert len(failed_ids) == 0

    @patch('trendradar.crawler.fetcher.requests.get')
    def test_crawl_websites_with_tuples(self, mock_get):
        """测试使用元组形式的 ID 列表"""
        mock_response = Mock()
        mock_response.text = json.dumps({
            "status": "success",
            "items": [{"title": "Test", "url": "http://example.com"}]
        })
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        fetcher = DataFetcher()
        results, id_to_name, failed_ids = fetcher.crawl_websites(
            [("id1", "Source One"), ("id2", "Source Two")],
            request_interval=0
        )

        assert id_to_name["id1"] == "Source One"
        assert id_to_name["id2"] == "Source Two"

    @patch('trendradar.crawler.fetcher.requests.get')
    def test_crawl_websites_with_failure(self, mock_get):
        """测试部分网站失败的情况"""
        mock_success = Mock()
        mock_success.text = json.dumps({
            "status": "success",
            "items": [{"title": "Test", "url": "http://example.com"}]
        })
        mock_success.raise_for_status = Mock()

        mock_fail = Mock()
        mock_fail.raise_for_status.side_effect = requests.RequestException("Network error")

        mock_get.side_effect = [mock_success, mock_fail]

        fetcher = DataFetcher()
        results, id_to_name, failed_ids = fetcher.crawl_websites(
            ["success_id", "fail_id"],
            request_interval=0
        )

        assert "success_id" in results
        assert "fail_id" not in results
        assert "fail_id" in failed_ids
        assert len(failed_ids) == 1

    @patch('trendradar.crawler.fetcher.requests.get')
    def test_crawl_websites_skip_invalid_titles(self, mock_get):
        """测试跳过无效标题"""
        mock_response = Mock()
        mock_response.text = json.dumps({
            "status": "success",
            "items": [
                {"title": "Valid Title", "url": "http://example.com/1"},
                {"title": None, "url": "http://example.com/2"},  # None 标题
                {"title": 123.45, "url": "http://example.com/3"},  # float 标题
                {"title": "   ", "url": "http://example.com/4"},  # 空字符串标题
                {"title": "Another Valid", "url": "http://example.com/5"},
            ]
        })
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        fetcher = DataFetcher()
        results, _, _ = fetcher.crawl_websites(["test_id"])

        assert len(results["test_id"]) == 2  # 只有两个有效标题
        assert "Valid Title" in results["test_id"]
        assert "Another Valid" in results["test_id"]

    @patch('trendradar.crawler.fetcher.requests.get')
    def test_crawl_websites_duplicate_titles(self, mock_get):
        """测试重复标题的处理"""
        mock_response = Mock()
        mock_response.text = json.dumps({
            "status": "success",
            "items": [
                {"title": "Duplicate Title", "url": "http://example.com/1"},
                {"title": "Duplicate Title", "url": "http://example.com/2"},
            ]
        })
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        fetcher = DataFetcher()
        results, _, _ = fetcher.crawl_websites(["test_id"])

        # 重复标题应该合并，ranks 包含两个排名
        assert len(results["test_id"]) == 1
        assert "Duplicate Title" in results["test_id"]
        assert len(results["test_id"]["Duplicate Title"]["ranks"]) == 2
        assert results["test_id"]["Duplicate Title"]["ranks"] == [1, 2]

    @patch('trendradar.crawler.fetcher.requests.get')
    def test_crawl_websites_invalid_json(self, mock_get):
        """测试无效 JSON 响应"""
        mock_response = Mock()
        mock_response.text = "invalid json"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        fetcher = DataFetcher()
        results, id_to_name, failed_ids = fetcher.crawl_websites(["test_id"])

        assert "test_id" not in results
        assert "test_id" in failed_ids

    @patch('trendradar.crawler.fetcher.requests.get')
    @patch('trendradar.crawler.fetcher.time.sleep')
    def test_crawl_websites_request_interval(self, mock_sleep, mock_get):
        """测试请求间隔"""
        mock_response = Mock()
        mock_response.text = json.dumps({
            "status": "success",
            "items": []
        })
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        fetcher = DataFetcher()
        fetcher.crawl_websites(["id1", "id2", "id3"], request_interval=100)

        # 3个ID，应该有2次间隔（最后一次不需要等待）
        assert mock_sleep.call_count == 2

    def test_default_api_url(self):
        """测试默认 API URL"""
        assert DataFetcher.DEFAULT_API_URL == "https://newsnow.busiyi.world/api/s"

    def test_default_headers(self):
        """测试默认请求头"""
        headers = DataFetcher.DEFAULT_HEADERS
        assert "User-Agent" in headers
        assert "Accept" in headers
        assert "Accept-Language" in headers
        assert "Connection" in headers
        assert "Cache-Control" in headers


class TestDataFetcherEdgeCases:
    """DataFetcher 边界情况测试"""

    @patch('trendradar.crawler.fetcher.requests.get')
    def test_empty_items_list(self, mock_get):
        """测试空 items 列表"""
        mock_response = Mock()
        mock_response.text = json.dumps({
            "status": "success",
            "items": []
        })
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        fetcher = DataFetcher()
        results, _, _ = fetcher.crawl_websites(["test_id"])

        assert "test_id" in results
        assert len(results["test_id"]) == 0

    @patch('trendradar.crawler.fetcher.requests.get')
    def test_items_with_missing_url(self, mock_get):
        """测试缺少 URL 字段的项目"""
        mock_response = Mock()
        mock_response.text = json.dumps({
            "status": "success",
            "items": [
                {"title": "Test"},  # 缺少 url 和 mobileUrl
            ]
        })
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        fetcher = DataFetcher()
        results, _, _ = fetcher.crawl_websites(["test_id"])

        assert "Test" in results["test_id"]
        assert results["test_id"]["Test"]["url"] == ""
        assert results["test_id"]["Test"]["mobileUrl"] == ""

    @patch('trendradar.crawler.fetcher.requests.get')
    def test_crawl_empty_ids_list(self, mock_get):
        """测试空 ID 列表"""
        fetcher = DataFetcher()
        results, id_to_name, failed_ids = fetcher.crawl_websites([])

        assert len(results) == 0
        assert len(id_to_name) == 0
        assert len(failed_ids) == 0
        mock_get.assert_not_called()

    @patch('trendradar.crawler.fetcher.requests.get')
    def test_fetch_data_unknown_status(self, mock_get):
        """测试未知状态"""
        mock_response = Mock()
        mock_response.text = '{"status": "unknown", "items": []}'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        fetcher = DataFetcher()
        data, id_value, alias = fetcher.fetch_data("test_id", max_retries=0)

        assert data is None
        assert id_value == "test_id"
