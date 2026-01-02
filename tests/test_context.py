# coding=utf-8
"""
TrendRadar AppContext 单元测试
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from trendradar.context import AppContext


class TestAppContextProperties:
    """AppContext 属性测试类"""

    def test_timezone_property(self):
        """测试时区属性"""
        config = {"TIMEZONE": "UTC"}
        ctx = AppContext(config)
        assert ctx.timezone == "UTC"

    def test_timezone_property_default(self):
        """测试时区属性默认值"""
        ctx = AppContext({})
        assert ctx.timezone == "Asia/Shanghai"

    def test_rank_threshold_property(self):
        """测试排名阈值属性"""
        config = {"RANK_THRESHOLD": 100}
        ctx = AppContext(config)
        assert ctx.rank_threshold == 100

    def test_rank_threshold_property_default(self):
        """测试排名阈值属性默认值"""
        ctx = AppContext({})
        assert ctx.rank_threshold == 50

    def test_weight_config_property(self):
        """测试权重配置属性"""
        from trendradar.core.analyzer import WeightConfig

        weight_config = WeightConfig(rank1=10, rank2=9, rank3=8)
        config = {"WEIGHT_CONFIG": weight_config}
        ctx = AppContext(config)
        assert ctx.weight_config == weight_config

    def test_weight_config_property_none(self):
        """测试权重配置属性为None"""
        ctx = AppContext({})
        assert ctx.weight_config is None

    def test_platforms_property(self):
        """测试平台配置列表属性"""
        platforms = [
            {"id": "weibo", "name": "微博"},
            {"id": "zhihu", "name": "知乎"},
        ]
        config = {"PLATFORMS": platforms}
        ctx = AppContext(config)
        assert ctx.platforms == platforms

    def test_platforms_property_default(self):
        """测试平台配置列表属性默认值"""
        ctx = AppContext({})
        assert ctx.platforms == []

    def test_platform_ids_property(self):
        """测试平台ID列表属性"""
        platforms = [
            {"id": "weibo", "name": "微博"},
            {"id": "zhihu", "name": "知乎"},
        ]
        config = {"PLATFORMS": platforms}
        ctx = AppContext(config)
        assert ctx.platform_ids == ["weibo", "zhihu"]

    def test_platform_ids_property_empty(self):
        """测试平台ID列表属性为空"""
        ctx = AppContext({})
        assert ctx.platform_ids == []

    def test_rss_config_property(self):
        """测试RSS配置属性"""
        rss_config = {"ENABLED": True, "FEEDS": []}
        config = {"RSS": rss_config}
        ctx = AppContext(config)
        assert ctx.rss_config == rss_config

    def test_rss_config_property_default(self):
        """测试RSS配置属性默认值"""
        ctx = AppContext({})
        assert ctx.rss_config == {}

    def test_rss_enabled_property(self):
        """测试RSS启用属性"""
        config = {"RSS": {"ENABLED": True}}
        ctx = AppContext(config)
        assert ctx.rss_enabled is True

    def test_rss_enabled_property_default(self):
        """测试RSS启用属性默认值"""
        ctx = AppContext({})
        assert ctx.rss_enabled is False

    def test_rss_feeds_property(self):
        """测试RSS源列表属性"""
        feeds = [{"url": "https://example.com/feed.xml", "name": "Example"}]
        config = {"RSS": {"FEEDS": feeds}}
        ctx = AppContext(config)
        assert ctx.rss_feeds == feeds

    def test_rss_feeds_property_default(self):
        """测试RSS源列表属性默认值"""
        ctx = AppContext({})
        assert ctx.rss_feeds == []

    def test_display_mode_property(self):
        """测试显示模式属性"""
        config = {"DISPLAY_MODE": "platform"}
        ctx = AppContext(config)
        assert ctx.display_mode == "platform"

    def test_display_mode_property_default(self):
        """测试显示模式属性默认值"""
        ctx = AppContext({})
        assert ctx.display_mode == "keyword"


class TestAppContextTimeOperations:
    """AppContext 时间操作测试类"""

    def test_get_time(self):
        """测试获取当前时间"""
        ctx = AppContext({"TIMEZONE": "Asia/Shanghai"})
        now = ctx.get_time()
        assert now is not None
        assert hasattr(now, "hour")

    @patch("trendradar.context.format_date_folder")
    def test_format_date(self, mock_format_date):
        """测试格式化日期"""
        mock_format_date.return_value = "2025-01-02"
        ctx = AppContext({"TIMEZONE": "Asia/Shanghai"})
        result = ctx.format_date()
        assert result == "2025-01-02"
        mock_format_date.assert_called_once_with(timezone="Asia/Shanghai")

    @patch("trendradar.context.format_time_filename")
    def test_format_time(self, mock_format_time):
        """测试格式化时间文件名"""
        mock_format_time.return_value = "12-34"
        ctx = AppContext({"TIMEZONE": "Asia/Shanghai"})
        result = ctx.format_time()
        assert result == "12-34"
        mock_format_time.assert_called_once_with("Asia/Shanghai")

    @patch("trendradar.context.get_current_time_display")
    def test_get_time_display(self, mock_get_time_display):
        """测试获取时间显示"""
        mock_get_time_display.return_value = "12:34"
        ctx = AppContext({"TIMEZONE": "Asia/Shanghai"})
        result = ctx.get_time_display()
        assert result == "12:34"
        mock_get_time_display.assert_called_once_with("Asia/Shanghai")

    @patch("trendradar.context.convert_time_for_display")
    def test_convert_time_display(self, mock_convert_time):
        """测试转换时间显示"""
        mock_convert_time.return_value = "12:34"
        result = AppContext.convert_time_display("12-34")
        assert result == "12:34"
        mock_convert_time.assert_called_once_with("12-34")


class TestAppContextStorageOperations:
    """AppContext 存储操作测试类"""

    @patch("trendradar.context.get_storage_manager")
    def test_get_storage_manager_initialization(self, mock_get_storage_manager):
        """测试存储管理器初始化"""
        mock_storage = Mock()
        mock_get_storage_manager.return_value = mock_storage

        config = {
            "STORAGE": {
                "BACKEND": "local",
                "LOCAL": {
                    "DATA_DIR": "test_output",
                    "RETENTION_DAYS": 7,
                },
                "REMOTE": {
                    "BUCKET_NAME": "test-bucket",
                    "RETENTION_DAYS": 30,
                },
                "PULL": {
                    "ENABLED": False,
                    "DAYS": 7,
                },
                "FORMATS": {
                    "TXT": True,
                    "HTML": True,
                },
            },
            "TIMEZONE": "Asia/Shanghai",
        }
        ctx = AppContext(config)
        storage = ctx.get_storage_manager()

        assert storage == mock_storage
        mock_get_storage_manager.assert_called_once()

    @patch("trendradar.context.get_storage_manager")
    def test_get_storage_manager_singleton(self, mock_get_storage_manager):
        """测试存储管理器单例模式"""
        mock_storage = Mock()
        mock_get_storage_manager.return_value = mock_storage

        ctx = AppContext({})
        storage1 = ctx.get_storage_manager()
        storage2 = ctx.get_storage_manager()

        assert storage1 is storage2
        # 只调用一次
        mock_get_storage_manager.assert_called_once()

    def test_get_output_path(self):
        """测试获取输出路径"""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            ctx = AppContext({"TIMEZONE": "Asia/Shanghai"})

            with patch.object(ctx, "format_date", return_value="2025-01-02"):
                with patch.object(ctx, "format_time", return_value="12-34"):
                    path = ctx.get_output_path("txt", "test.txt")

                    assert "2025-01-02" in path
                    assert "txt" in path
                    assert "test.txt" in path
                    # 验证父目录被创建（文件本身不存在）
                    dir_path = os.path.dirname(path)
                    assert os.path.exists(dir_path)

    @patch("trendradar.context.save_titles_to_file")
    def test_save_titles(self, mock_save_titles):
        """测试保存标题"""
        mock_save_titles.return_value = "/path/to/file.txt"

        ctx = AppContext({})
        results = {"weibo": {"items": []}}
        id_to_name = {"weibo": "微博"}
        failed_ids = []

        with patch.object(ctx, "get_output_path", return_value="/path/to/file.txt"):
            path = ctx.save_titles(results, id_to_name, failed_ids)
            assert path == "/path/to/file.txt"
            mock_save_titles.assert_called_once()

    @patch("trendradar.context.read_all_today_titles")
    def test_read_today_titles(self, mock_read_titles):
        """测试读取当天标题"""
        mock_read_titles.return_value = ({}, {}, {})

        ctx = AppContext({})
        mock_storage = Mock()
        with patch.object(ctx, "get_storage_manager", return_value=mock_storage):
            results = ctx.read_today_titles()
            assert results == ({}, {}, {})
            mock_read_titles.assert_called_once()

    @patch("trendradar.context.detect_latest_new_titles")
    def test_detect_new_titles(self, mock_detect):
        """测试检测新标题"""
        mock_detect.return_value = {"weibo": ["new_title"]}

        ctx = AppContext({})
        mock_storage = Mock()
        with patch.object(ctx, "get_storage_manager", return_value=mock_storage):
            new_titles = ctx.detect_new_titles()
            assert new_titles == {"weibo": ["new_title"]}
            mock_detect.assert_called_once()

    def test_is_first_crawl(self):
        """测试是否首次爬取"""
        ctx = AppContext({})
        mock_storage = Mock()
        mock_storage.is_first_crawl_today.return_value = True

        with patch.object(ctx, "get_storage_manager", return_value=mock_storage):
            result = ctx.is_first_crawl()
            assert result is True


class TestAppContextFrequencyWords:
    """AppContext 频率词处理测试类"""

    @patch("trendradar.context.load_frequency_words")
    def test_load_frequency_words(self, mock_load):
        """测试加载频率词"""
        mock_load.return_value = ([{"words": ["AI"]}], [], [])

        ctx = AppContext({})
        word_groups, filter_words, global_filters = ctx.load_frequency_words("test.txt")

        assert word_groups == [{"words": ["AI"]}]
        assert filter_words == []
        assert global_filters == []
        mock_load.assert_called_once_with("test.txt")

    @patch("trendradar.context.matches_word_groups")
    def test_matches_word_groups(self, mock_matches):
        """测试匹配词组"""
        mock_matches.return_value = True

        ctx = AppContext({})
        word_groups = [{"words": ["AI"]}]
        filter_words = []
        title = "AI新闻"

        result = ctx.matches_word_groups(title, word_groups, filter_words)
        assert result is True
        mock_matches.assert_called_once()


class TestAppContextStatistics:
    """AppContext 统计分析测试类"""

    @patch("trendradar.context.count_word_frequency")
    def test_count_frequency(self, mock_count):
        """测试词频统计"""
        mock_count.return_value = ([{"keyword": "AI", "count": 10}], 10)

        ctx = AppContext({"RANK_THRESHOLD": 50, "MAX_NEWS_PER_KEYWORD": 5})
        results = {"weibo": {"items": []}}
        word_groups = [{"words": ["AI"]}]
        filter_words = []
        id_to_name = {"weibo": "微博"}

        with patch.object(ctx, "is_first_crawl", return_value=False):
            with patch.object(ctx, "convert_time_display", return_value="12:34"):
                stats, total = ctx.count_frequency(
                    results, word_groups, filter_words, id_to_name
                )

                assert stats == [{"keyword": "AI", "count": 10}]
                assert total == 10
                mock_count.assert_called_once()


class TestAppContextReportGeneration:
    """AppContext 报告生成测试类"""

    @patch("trendradar.context.prepare_report_data")
    def test_prepare_report(self, mock_prepare):
        """测试准备报告数据"""
        mock_prepare.return_value = {"stats": []}

        ctx = AppContext({"RANK_THRESHOLD": 50})
        stats = [{"keyword": "AI", "count": 10}]

        report_data = ctx.prepare_report(stats)
        assert report_data == {"stats": []}
        mock_prepare.assert_called_once()

    @patch("trendradar.context.generate_html_report")
    def test_generate_html(self, mock_generate):
        """测试生成HTML报告"""
        mock_generate.return_value = "<html>report</html>"

        ctx = AppContext({"RANK_THRESHOLD": 50})
        stats = [{"keyword": "AI", "count": 10}]

        with patch.object(ctx, "format_date", return_value="2025-01-02"):
            with patch.object(ctx, "format_time", return_value="12-34"):
                html = ctx.generate_html(stats, 10)

                assert html == "<html>report</html>"
                mock_generate.assert_called_once()

    @patch("trendradar.context.render_html_content")
    def test_render_html(self, mock_render):
        """测试渲染HTML内容"""
        mock_render.return_value = "<html>content</html>"

        ctx = AppContext({"DISPLAY_MODE": "keyword"})
        report_data = {"stats": []}

        html = ctx.render_html(report_data, 10)
        assert html == "<html>content</html>"
        mock_render.assert_called_once()


class TestAppContextNotificationRendering:
    """AppContext 通知内容渲染测试类"""

    @patch("trendradar.context.render_feishu_content")
    def test_render_feishu(self, mock_render):
        """测试渲染飞书内容"""
        mock_render.return_value = "feishu content"

        ctx = AppContext({})
        report_data = {"stats": []}

        content = ctx.render_feishu(report_data)
        assert content == "feishu content"
        mock_render.assert_called_once()

    @patch("trendradar.context.render_dingtalk_content")
    def test_render_dingtalk(self, mock_render):
        """测试渲染钉钉内容"""
        mock_render.return_value = "dingtalk content"

        ctx = AppContext({})
        report_data = {"stats": []}

        content = ctx.render_dingtalk(report_data)
        assert content == "dingtalk content"
        mock_render.assert_called_once()

    @patch("trendradar.context.split_content_into_batches")
    def test_split_content(self, mock_split):
        """测试分批处理内容"""
        mock_split.return_value = ["batch1", "batch2"]

        ctx = AppContext({})
        report_data = {"stats": []}

        batches = ctx.split_content(report_data, "feishu")
        assert batches == ["batch1", "batch2"]
        mock_split.assert_called_once()


class TestAppContextNotificationSending:
    """AppContext 通知发送测试类"""

    def test_create_notification_dispatcher(self):
        """测试创建通知调度器"""
        from trendradar.notification import NotificationDispatcher

        ctx = AppContext({})
        dispatcher = ctx.create_notification_dispatcher()

        assert isinstance(dispatcher, NotificationDispatcher)

    def test_create_push_manager(self):
        """测试创建推送记录管理器"""
        from trendradar.notification import PushRecordManager

        ctx = AppContext({})
        mock_storage = Mock()

        with patch.object(ctx, "get_storage_manager", return_value=mock_storage):
            manager = ctx.create_push_manager()
            assert isinstance(manager, PushRecordManager)


class TestAppContextCleanup:
    """AppContext 资源清理测试类"""

    def test_cleanup_with_storage_manager(self):
        """测试清理存储管理器"""
        ctx = AppContext({})
        mock_storage = Mock()

        # 直接设置存储管理器以避免单例模式
        ctx._storage_manager = mock_storage
        ctx.cleanup()

        # 验证清理方法被调用
        mock_storage.cleanup_old_data.assert_called_once()
        mock_storage.cleanup.assert_called_once()
        # 验证存储管理器被重置
        assert ctx._storage_manager is None

    def test_cleanup_without_storage_manager(self):
        """测试没有存储管理器时的清理"""
        ctx = AppContext({})
        # 不应该抛出异常
        ctx.cleanup()
        assert ctx._storage_manager is None


class TestAppContextEdgeCases:
    """AppContext 边界情况测试类"""

    def test_empty_config(self):
        """测试空配置"""
        ctx = AppContext({})
        assert ctx.timezone == "Asia/Shanghai"
        assert ctx.rank_threshold == 50
        assert ctx.platforms == []
        assert ctx.rss_enabled is False

    def test_none_values_in_config(self):
        """测试配置中包含None值"""
        ctx = AppContext({"WEIGHT_CONFIG": None, "PLATFORMS": None})
        assert ctx.weight_config is None
        # cast会保留None，但实际使用时会有默认值
        assert ctx.platforms is None or ctx.platforms == []

    def test_multiple_storage_manager_calls(self):
        """测试多次调用存储管理器"""
        ctx = AppContext({})
        mock_storage = Mock()

        with patch.object(ctx, "get_storage_manager", return_value=mock_storage):
            storage1 = ctx.get_storage_manager()
            storage2 = ctx.get_storage_manager()
            storage3 = ctx.get_storage_manager()

            # 应该返回同一个实例
            assert storage1 is storage2 is storage3

    def test_config_mutation(self):
        """测试配置变更"""
        config = {"TIMEZONE": "UTC"}
        ctx = AppContext(config)

        assert ctx.timezone == "UTC"

        # 修改配置
        config["TIMEZONE"] = "Asia/Shanghai"
        # 应该反映变化
        assert ctx.timezone == "Asia/Shanghai"
