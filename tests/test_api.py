# coding=utf-8
"""
TrendRadar API 单元测试
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from trendradar.core.api import TrendRadarAPI


class TestTrendRadarAPI:
    """TrendRadarAPI 测试类"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def api(self, temp_dir):
        """创建 API 实例"""
        return TrendRadarAPI(work_dir=temp_dir)

    @pytest.fixture
    def api_with_config(self, temp_dir):
        """创建带配置的 API 实例"""
        # 创建配置文件
        config_content = """
PLATFORMS:
  - id: zhihu
    name: 知乎
  - id: weibo
    name: 微博

REQUEST_INTERVAL: 1000
TIMEZONE: Asia/Shanghai
REPORT_MODE: daily
RANK_THRESHOLD: 5

STORAGE:
  BACKEND: local
  DATA_DIR: output
  FORMATS:
    SQLITE: true
    TXT: false
    HTML: true

WEIGHT:
  RANK: 0.6
  FREQUENCY: 0.3
  HOTNESS: 0.1
"""
        config_path = Path(temp_dir) / "config.yaml"
        config_path.write_text(config_content, encoding="utf-8")

        return TrendRadarAPI(config_path=str(config_path), work_dir=temp_dir)

    def test_init_with_defaults(self, api):
        """测试默认初始化"""
        assert api.config is not None
        assert api.work_dir is not None
        assert api.fetcher is not None
        assert api.storage is not None

    def test_init_with_config(self, api_with_config):
        """测试使用配置文件初始化"""
        assert api_with_config.config is not None
        assert "PLATFORMS" in api_with_config.config
        assert len(api_with_config.config["PLATFORMS"]) == 2

    def test_get_default_config(self, api):
        """测试获取默认配置"""
        config = api._get_default_config()
        assert "PLATFORMS" in config
        assert "REQUEST_INTERVAL" in config
        assert "STORAGE" in config
        assert len(config["PLATFORMS"]) == 3  # 默认3个平台

    def test_filter_by_keywords_any(self, api):
        """测试关键词过滤 - 任意匹配"""
        news_data = [
            {"title": "人工智能新技术", "url": "http://example.com/1"},
            {"title": "今日天气预报", "url": "http://example.com/2"},
            {"title": "AI模型突破", "url": "http://example.com/3"},
        ]

        keywords = ["人工智能", "AI"]
        filtered = api.filter_by_keywords(news_data, keywords, match_type="any")

        assert len(filtered) == 2
        assert filtered[0]["title"] == "人工智能新技术"
        assert filtered[1]["title"] == "AI模型突破"

    def test_filter_by_keywords_all(self, api):
        """测试关键词过滤 - 全部匹配"""
        news_data = [
            {"title": "人工智能AI技术", "url": "http://example.com/1"},
            {"title": "人工智能发展", "url": "http://example.com/2"},
            {"title": "AI模型", "url": "http://example.com/3"},
        ]

        keywords = ["人工智能", "AI"]
        filtered = api.filter_by_keywords(news_data, keywords, match_type="all")

        assert len(filtered) == 1
        assert filtered[0]["title"] == "人工智能AI技术"

    def test_filter_by_keywords_no_match(self, api):
        """测试关键词过滤 - 无匹配"""
        news_data = [
            {"title": "今日天气预报", "url": "http://example.com/1"},
            {"title": "体育新闻", "url": "http://example.com/2"},
        ]

        keywords = ["人工智能", "AI"]
        filtered = api.filter_by_keywords(news_data, keywords)

        assert len(filtered) == 0

    def test_load_keywords(self, temp_dir):
        """测试加载关键词文件"""
        # 创建关键词文件
        keywords_content = """# 测试关键词
人工智能
AI
科技

+技术
!广告
"""
        keywords_path = Path(temp_dir) / "keywords.txt"
        keywords_path.write_text(keywords_content, encoding="utf-8")

        api = TrendRadarAPI(keywords_path=str(keywords_path), work_dir=temp_dir)

        assert len(api.keywords) > 0
        assert len(api.filter_words) > 0

    def test_analyze_news_without_data(self, api):
        """测试无数据时的分析"""
        result = api.analyze_news()

        # 应该返回错误信息
        assert "error" in result

    def test_get_hot_topics_empty(self, api):
        """测试获取热点话题 - 无数据"""
        hot_topics = api.get_hot_topics()

        # 无数据时返回空列表
        assert hot_topics == []

    def test_get_news_by_date(self, api):
        """测试按日期获取新闻"""
        # 这需要实际的数据，这里只测试方法调用
        news = api.get_news_by_date("2025-01-02")

        # 可能返回 None 或空列表
        assert news is None or isinstance(news, list)

    def test_export_html_without_data(self, api):
        """测试导出HTML - 无数据"""
        html_path = api.export_html()

        # 无数据时应该返回 None
        assert html_path is None


@pytest.mark.integration
class TestTrendRadarAPIIntegration:
    """TrendRadarAPI 集成测试（需要网络）"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def api(self, temp_dir):
        """创建 API 实例"""
        return TrendRadarAPI(work_dir=temp_dir)

    def test_fetch_news(self, api):
        """测试抓取新闻（需要网络）"""
        # 只抓取一个平台，减少测试时间
        news = api.fetch_news(platforms=["zhihu"])

        assert isinstance(news, list)
        # 即使失败也应该返回空列表
        assert len(news) >= 0

    @pytest.mark.skip(reason="需要实际数据支持")
    def test_full_workflow(self, api):
        """测试完整工作流"""
        # 1. 抓取新闻
        news = api.fetch_news(platforms=["zhihu"])
        assert len(news) > 0

        # 2. 分析新闻
        result = api.analyze_news()
        assert "stats" in result
        assert "total" in result

        # 3. 获取热点话题
        hot_topics = api.get_hot_topics(top_n=5)
        assert len(hot_topics) > 0

        # 4. 导出HTML
        html_path = api.export_html()
        assert html_path is not None
        assert Path(html_path).exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
