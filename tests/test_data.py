# coding=utf-8
"""
测试数据处理模块 (trendradar/core/data.py)

Author: TrendRadar Team
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, List
from unittest.mock import Mock, MagicMock, patch, PropertyMock

import pytest

from trendradar.core.data import (
    save_titles_to_file,
    read_all_today_titles_from_storage,
    read_all_today_titles,
    detect_latest_new_titles_from_storage,
    detect_latest_new_titles,
    is_first_crawl_today,
)
from trendradar.storage.base import NewsData, NewsItem


class TestSaveTitlesToFile:
    """测试 save_titles_to_file 函数"""

    def test_save_basic_data(self, tmp_path):
        """测试基本数据保存"""
        results = {
            "baidu": {
                "Python教程": {"ranks": [1], "url": "http://example.com/1", "mobileUrl": "http://m.example.com/1"}
            }
        }
        id_to_name = {"baidu": "百度热榜"}
        failed_ids = []
        output_path = tmp_path / "output.txt"

        def clean_title(title: str) -> str:
            return title.strip()

        result = save_titles_to_file(results, id_to_name, failed_ids, str(output_path), clean_title)

        assert result == str(output_path)
        assert output_path.exists()

        content = output_path.read_text(encoding="utf-8")
        assert "baidu | 百度热榜" in content
        assert "1. Python教程" in content
        assert "[URL:http://example.com/1]" in content
        assert "[MOBILE:http://m.example.com/1]" in content

    def test_save_with_id_only(self, tmp_path):
        """测试只有ID没有名称的情况"""
        results = {
            "weibo": {
                "热搜话题": {"ranks": [1], "url": "", "mobileUrl": ""}
            }
        }
        id_to_name = {"weibo": "weibo"}  # name equals id
        failed_ids = []
        output_path = tmp_path / "output.txt"

        result = save_titles_to_file(results, id_to_name, failed_ids, str(output_path), lambda x: x)

        assert result == str(output_path)
        content = output_path.read_text(encoding="utf-8")
        assert "weibo\n" in content  # Should only write ID, not "weibo | weibo"

    def test_save_with_failed_ids(self, tmp_path):
        """测试保存失败的ID"""
        results = {}
        id_to_name = {}
        failed_ids = ["zhihu", "douban"]
        output_path = tmp_path / "output.txt"

        result = save_titles_to_file(results, id_to_name, failed_ids, str(output_path), lambda x: x)

        assert result == str(output_path)
        content = output_path.read_text(encoding="utf-8")
        assert "==== 以下ID请求失败 ====" in content
        assert "zhihu" in content
        assert "douban" in content

    def test_save_with_list_format_info(self, tmp_path):
        """测试info为list格式的情况"""
        results = {
            "baidu": {
                "测试标题": [1, 2, 3]  # list format instead of dict
            }
        }
        id_to_name = {}
        failed_ids = []
        output_path = tmp_path / "output.txt"

        result = save_titles_to_file(results, id_to_name, failed_ids, str(output_path), lambda x: x)

        assert result == str(output_path)
        content = output_path.read_text(encoding="utf-8")
        assert "1. 测试标题" in content

    def test_save_creates_directory(self, tmp_path):
        """测试自动创建目录"""
        results = {"test": {"标题": {"ranks": [1], "url": "", "mobileUrl": ""}}}
        id_to_name = {}
        failed_ids = []
        output_path = tmp_path / "deep" / "nested" / "output.txt"

        result = save_titles_to_file(results, id_to_name, failed_ids, str(output_path), lambda x: x)

        assert result == str(output_path)
        assert output_path.exists()
        assert output_path.parent.exists()

    def test_save_sorts_titles_by_rank(self, tmp_path):
        """测试按排名排序标题"""
        results = {
            "baidu": {
                "标题3": {"ranks": [3], "url": "", "mobileUrl": ""},
                "标题1": {"ranks": [1], "url": "", "mobileUrl": ""},
                "标题2": {"ranks": [2], "url": "", "mobileUrl": ""},
            }
        }
        id_to_name = {}
        failed_ids = []
        output_path = tmp_path / "output.txt"

        save_titles_to_file(results, id_to_name, failed_ids, str(output_path), lambda x: x)

        content = output_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        # Find the lines with titles
        title_lines = [line for line in lines if "标题" in line]
        assert title_lines[0].startswith("1. 标题1")
        assert title_lines[1].startswith("2. 标题2")
        assert title_lines[2].startswith("3. 标题3")

    def test_save_with_empty_ranks(self, tmp_path):
        """测试空排名列表"""
        results = {
            "baidu": {
                "无排名标题": {"ranks": [], "url": "", "mobileUrl": ""}
            }
        }
        id_to_name = {}
        failed_ids = []
        output_path = tmp_path / "output.txt"

        save_titles_to_file(results, id_to_name, failed_ids, str(output_path), lambda x: x)

        content = output_path.read_text(encoding="utf-8")
        # Empty ranks should default to rank 1
        assert "1. 无排名标题" in content

    def test_save_applies_clean_title_func(self, tmp_path):
        """测试应用标题清理函数"""
        results = {
            "baidu": {
                "  标题  ": {"ranks": [1], "url": "", "mobileUrl": ""}
            }
        }
        id_to_name = {}
        failed_ids = []
        output_path = tmp_path / "output.txt"

        def strip_spaces(title: str) -> str:
            return title.strip()

        save_titles_to_file(results, id_to_name, failed_ids, str(output_path), strip_spaces)

        content = output_path.read_text(encoding="utf-8")
        assert "1. 标题" in content  # Spaces should be removed
        assert "1.   标题  " not in content


class TestReadAllTodayTitlesFromStorage:
    """测试 read_all_today_titles_from_storage 函数"""

    def test_read_basic_data(self):
        """测试基本数据读取"""
        mock_storage = Mock()
        mock_news_data = Mock(spec=NewsData)
        mock_news_data.items = {
            "baidu": [
                NewsItem(source_id="test",
                    title="Python教程",
                    rank=1,
                    url="http://example.com",
                    mobile_url="http://m.example.com",
                    crawl_time="2026-01-02 10:00:00",
                )
            ]
        }
        mock_news_data.id_to_name = {"baidu": "百度热榜"}
        mock_storage.get_today_all_data.return_value = mock_news_data

        results, id_to_name, title_info = read_all_today_titles_from_storage(mock_storage)

        assert "baidu" in results
        assert "Python教程" in results["baidu"]
        assert id_to_name["baidu"] == "百度热榜"
        assert "baidu" in title_info
        assert "Python教程" in title_info["baidu"]

    def test_read_with_platform_filter(self):
        """测试平台过滤"""
        mock_storage = Mock()
        mock_news_data = Mock(spec=NewsData)
        mock_news_data.items = {
            "baidu": [NewsItem(source_id="test", title="标题1", rank=1, crawl_time="2026-01-02 10:00:00")],
            "weibo": [NewsItem(source_id="test", title="标题2", rank=1, crawl_time="2026-01-02 10:00:00")],
        }
        mock_news_data.id_to_name = {"baidu": "百度", "weibo": "微博"}
        mock_storage.get_today_all_data.return_value = mock_news_data

        results, id_to_name, title_info = read_all_today_titles_from_storage(
            mock_storage, current_platform_ids=["baidu"]
        )

        assert "baidu" in results
        assert "weibo" not in results

    def test_read_empty_data(self):
        """测试空数据"""
        mock_storage = Mock()
        mock_storage.get_today_all_data.return_value = None

        results, id_to_name, title_info = read_all_today_titles_from_storage(mock_storage)

        assert results == {}
        assert id_to_name == {}
        assert title_info == {}

    def test_read_empty_items(self):
        """测试空items"""
        mock_storage = Mock()
        mock_news_data = Mock(spec=NewsData)
        mock_news_data.items = {}
        mock_storage.get_today_all_data.return_value = mock_news_data

        results, id_to_name, title_info = read_all_today_titles_from_storage(mock_storage)

        assert results == {}
        assert id_to_name == {}
        assert title_info == {}

    def test_read_with_additional_attributes(self):
        """测试带额外属性的数据"""
        mock_storage = Mock()
        mock_news_data = Mock(spec=NewsData)
        item = NewsItem(source_id="test",
            title="测试标题",
            rank=1,
            url="http://example.com",
            mobile_url="http://m.example.com",
            crawl_time="2026-01-02 10:00:00",
        )
        # Add additional attributes
        item.ranks = [1, 2, 3]
        item.first_time = "2026-01-02 09:00:00"
        item.last_time = "2026-01-02 10:00:00"
        item.count = 2

        mock_news_data.items = {"baidu": [item]}
        mock_news_data.id_to_name = {"baidu": "百度"}
        mock_storage.get_today_all_data.return_value = mock_news_data

        results, id_to_name, title_info = read_all_today_titles_from_storage(mock_storage)

        assert results["baidu"]["测试标题"]["ranks"] == [1, 2, 3]
        assert title_info["baidu"]["测试标题"]["first_time"] == "2026-01-02 09:00:00"
        assert title_info["baidu"]["测试标题"]["last_time"] == "2026-01-02 10:00:00"
        assert title_info["baidu"]["测试标题"]["count"] == 2

    def test_read_with_exception(self):
        """测试异常处理"""
        mock_storage = Mock()
        mock_storage.get_today_all_data.side_effect = Exception("Database error")

        results, id_to_name, title_info = read_all_today_titles_from_storage(mock_storage)

        assert results == {}
        assert id_to_name == {}
        assert title_info == {}

    def test_read_without_id_to_name(self):
        """测试没有id_to_name的情况"""
        mock_storage = Mock()
        mock_news_data = Mock(spec=NewsData)
        mock_news_data.items = {
            "unknown_id": [NewsItem(source_id="test", title="标题", rank=1, crawl_time="2026-01-02 10:00:00")]
        }
        mock_news_data.id_to_name = {}
        mock_storage.get_today_all_data.return_value = mock_news_data

        results, id_to_name, title_info = read_all_today_titles_from_storage(mock_storage)

        # Should use source_id as name
        assert id_to_name["unknown_id"] == "unknown_id"


class TestReadAllTodayTitles:
    """测试 read_all_today_titles 函数"""

    def test_read_with_logging(self, capsys):
        """测试带日志输出的读取"""
        mock_storage = Mock()
        mock_news_data = Mock(spec=NewsData)
        mock_news_data.items = {
            "baidu": [
                NewsItem(source_id="test", title="标题1", rank=1, crawl_time="2026-01-02 10:00:00"),
                NewsItem(source_id="test", title="标题2", rank=2, crawl_time="2026-01-02 10:00:00"),
            ]
        }
        mock_news_data.id_to_name = {"baidu": "百度"}
        mock_storage.get_today_all_data.return_value = mock_news_data

        results, id_to_name, title_info = read_all_today_titles(mock_storage, quiet=False)

        captured = capsys.readouterr()
        assert "已从存储后端读取 2 条标题" in captured.out

    def test_read_with_no_data_logging(self, capsys):
        """测试无数据时的日志"""
        mock_storage = Mock()
        mock_storage.get_today_all_data.return_value = None

        results, id_to_name, title_info = read_all_today_titles(mock_storage, quiet=False)

        captured = capsys.readouterr()
        assert "当天暂无数据" in captured.out

    def test_read_quiet_mode(self, capsys):
        """测试静默模式"""
        mock_storage = Mock()
        mock_news_data = Mock(spec=NewsData)
        mock_news_data.items = {
            "baidu": [NewsItem(source_id="test", title="标题", rank=1, crawl_time="2026-01-02 10:00:00")]
        }
        mock_news_data.id_to_name = {"baidu": "百度"}
        mock_storage.get_today_all_data.return_value = mock_news_data

        results, id_to_name, title_info = read_all_today_titles(mock_storage, quiet=True)

        captured = capsys.readouterr()
        assert "已从存储后端读取" not in captured.out


class TestDetectLatestNewTitlesFromStorage:
    """测试 detect_latest_new_titles_from_storage 函数"""

    def test_detect_new_titles_basic(self):
        """测试基本的新标题检测"""
        mock_storage = Mock()

        # Latest data (new batch)
        mock_latest = Mock(spec=NewsData)
        mock_latest.crawl_time = "2026-01-02 12:00:00"
        mock_latest.items = {
            "baidu": [
                NewsItem(source_id="test",
                    title="新标题",
                    rank=1,
                    url="http://example.com/new",
                    mobile_url="http://m.example.com/new",
                    crawl_time="2026-01-02 12:00:00",
                )
            ]
        }

        # All data (historical + new)
        mock_all = Mock(spec=NewsData)
        mock_all.items = {
            "baidu": [
                NewsItem(source_id="test",
                    title="旧标题",
                    rank=1,
                    crawl_time="2026-01-02 10:00:00",
                ),
                # Add first_time attribute to mark it as historical
                NewsItem(source_id="test",
                    title="新标题",
                    rank=1,
                    crawl_time="2026-01-02 12:00:00",
                )
            ]
        }
        # Set first_time for historical item
        mock_all.items["baidu"][0].first_time = "2026-01-02 10:00:00"
        mock_all.items["baidu"][1].first_time = "2026-01-02 12:00:00"  # Same as latest, so it's new

        mock_storage.get_latest_crawl_data.return_value = mock_latest
        mock_storage.get_today_all_data.return_value = mock_all

        new_titles = detect_latest_new_titles_from_storage(mock_storage)

        assert "baidu" in new_titles
        assert "新标题" in new_titles["baidu"]

    def test_detect_no_new_titles(self):
        """测试没有新标题的情况"""
        mock_storage = Mock()

        mock_latest = Mock(spec=NewsData)
        mock_latest.crawl_time = "2026-01-02 12:00:00"
        mock_latest.items = {
            "baidu": [
                NewsItem(source_id="test", title="标题", rank=1, crawl_time="2026-01-02 12:00:00")
            ]
        }

        mock_all = Mock(spec=NewsData)
        item = NewsItem(source_id="test", title="标题", rank=1, crawl_time="2026-01-02 12:00:00")
        item.first_time = "2026-01-02 10:00:00"  # Historical
        mock_all.items = {"baidu": [item]}

        mock_storage.get_latest_crawl_data.return_value = mock_latest
        mock_storage.get_today_all_data.return_value = mock_all

        new_titles = detect_latest_new_titles_from_storage(mock_storage)

        assert new_titles == {}

    def test_detect_first_crawl_no_new_titles(self):
        """测试第一次抓取时无新标题"""
        mock_storage = Mock()

        mock_latest = Mock(spec=NewsData)
        mock_latest.crawl_time = "2026-01-02 12:00:00"
        mock_latest.items = {
            "baidu": [
                NewsItem(source_id="test", title="标题", rank=1, crawl_time="2026-01-02 12:00:00")
            ]
        }

        mock_all = Mock(spec=NewsData)
        item = NewsItem(source_id="test", title="标题", rank=1, crawl_time="2026-01-02 12:00:00")
        item.first_time = "2026-01-02 12:00:00"  # Same as latest, first crawl
        mock_all.items = {"baidu": [item]}

        mock_storage.get_latest_crawl_data.return_value = mock_latest
        mock_storage.get_today_all_data.return_value = mock_all

        new_titles = detect_latest_new_titles_from_storage(mock_storage)

        # First crawl should return empty
        assert new_titles == {}

    def test_detect_with_platform_filter(self):
        """测试带平台过滤的新标题检测"""
        mock_storage = Mock()

        mock_latest = Mock(spec=NewsData)
        mock_latest.crawl_time = "2026-01-02 12:00:00"
        mock_latest.items = {
            "baidu": [NewsItem(source_id="test", title="百度新", rank=1, crawl_time="2026-01-02 12:00:00")],
            "weibo": [NewsItem(source_id="test", title="微博新", rank=1, crawl_time="2026-01-02 12:00:00")],
        }

        mock_all = Mock(spec=NewsData)
        # Add historical item to baidu
        baidu_old = NewsItem(source_id="test", title="百度旧", rank=1, crawl_time="2026-01-02 10:00:00")
        baidu_old.first_time = "2026-01-02 10:00:00"
        # New item for baidu
        baidu_item = NewsItem(source_id="test", title="百度新", rank=1, crawl_time="2026-01-02 12:00:00")
        baidu_item.first_time = "2026-01-02 12:00:00"
        weibo_item = NewsItem(source_id="test", title="微博新", rank=1, crawl_time="2026-01-02 12:00:00")
        weibo_item.first_time = "2026-01-02 12:00:00"
        mock_all.items = {"baidu": [baidu_old, baidu_item], "weibo": [weibo_item]}

        mock_storage.get_latest_crawl_data.return_value = mock_latest
        mock_storage.get_today_all_data.return_value = mock_all

        new_titles = detect_latest_new_titles_from_storage(
            mock_storage, current_platform_ids=["baidu"]
        )

        assert "baidu" in new_titles
        assert "weibo" not in new_titles

    def test_detect_empty_latest_data(self):
        """测试空最新数据"""
        mock_storage = Mock()
        mock_storage.get_latest_crawl_data.return_value = None

        new_titles = detect_latest_new_titles_from_storage(mock_storage)

        assert new_titles == {}

    def test_detect_empty_all_data(self):
        """测试空历史数据"""
        mock_storage = Mock()

        mock_latest = Mock(spec=NewsData)
        mock_latest.crawl_time = "2026-01-02 12:00:00"
        mock_latest.items = {"baidu": [NewsItem(source_id="test", title="标题", rank=1, crawl_time="2026-01-02 12:00:00")]}

        mock_storage.get_latest_crawl_data.return_value = mock_latest
        mock_storage.get_today_all_data.return_value = None

        new_titles = detect_latest_new_titles_from_storage(mock_storage)

        assert new_titles == {}

    def test_detect_with_exception(self):
        """测试异常处理"""
        mock_storage = Mock()
        mock_storage.get_latest_crawl_data.side_effect = Exception("Error")

        new_titles = detect_latest_new_titles_from_storage(mock_storage)

        assert new_titles == {}


class TestDetectLatestNewTitles:
    """测试 detect_latest_new_titles 函数"""

    def test_detect_with_logging(self, capsys):
        """测试带日志的新标题检测"""
        mock_storage = Mock()

        mock_latest = Mock(spec=NewsData)
        mock_latest.crawl_time = "2026-01-02 12:00:00"
        mock_latest.items = {
            "baidu": [
                NewsItem(source_id="test", title="新标题1", rank=1, crawl_time="2026-01-02 12:00:00"),
                NewsItem(source_id="test", title="新标题2", rank=2, crawl_time="2026-01-02 12:00:00"),
            ]
        }

        mock_all = Mock(spec=NewsData)
        historical = NewsItem(source_id="test", title="旧标题", rank=1, crawl_time="2026-01-02 10:00:00")
        historical.first_time = "2026-01-02 10:00:00"
        new1 = NewsItem(source_id="test", title="新标题1", rank=1, crawl_time="2026-01-02 12:00:00")
        new1.first_time = "2026-01-02 12:00:00"
        new2 = NewsItem(source_id="test", title="新标题2", rank=2, crawl_time="2026-01-02 12:00:00")
        new2.first_time = "2026-01-02 12:00:00"
        mock_all.items = {"baidu": [historical, new1, new2]}

        mock_storage.get_latest_crawl_data.return_value = mock_latest
        mock_storage.get_today_all_data.return_value = mock_all

        new_titles = detect_latest_new_titles(mock_storage, quiet=False)

        captured = capsys.readouterr()
        assert "从存储后端检测到 2 条新增标题" in captured.out
        assert len(new_titles["baidu"]) == 2

    def test_detect_quiet_mode(self, capsys):
        """测试静默模式"""
        mock_storage = Mock()
        mock_storage.get_latest_crawl_data.return_value = None

        new_titles = detect_latest_new_titles(mock_storage, quiet=True)

        captured = capsys.readouterr()
        assert "从存储后端检测到" not in captured.out


class TestIsFirstCrawlToday:
    """测试 is_first_crawl_today 函数"""

    def test_first_crawl_no_directory(self, tmp_path):
        """测试没有目录的情况"""
        result = is_first_crawl_today(str(tmp_path), "2026-01-02")
        assert result is True

    def test_first_crawl_empty_directory(self, tmp_path):
        """测试空目录"""
        date_folder = tmp_path / "2026-01-02" / "txt"
        date_folder.mkdir(parents=True)

        result = is_first_crawl_today(str(tmp_path), "2026-01-02")
        assert result is True

    def test_first_crawl_one_file(self, tmp_path):
        """测试只有一个文件（第一次爬取）"""
        txt_dir = tmp_path / "2026-01-02" / "txt"
        txt_dir.mkdir(parents=True)
        (txt_dir / "snapshot_1.txt").touch()

        result = is_first_crawl_today(str(tmp_path), "2026-01-02")
        assert result is True

    def test_not_first_crawl_multiple_files(self, tmp_path):
        """测试有多个文件（非第一次爬取）"""
        txt_dir = tmp_path / "2026-01-02" / "txt"
        txt_dir.mkdir(parents=True)
        (txt_dir / "snapshot_1.txt").touch()
        (txt_dir / "snapshot_2.txt").touch()

        result = is_first_crawl_today(str(tmp_path), "2026-01-02")
        assert result is False

    def test_first_crawl_ignores_non_txt_files(self, tmp_path):
        """测试忽略非txt文件"""
        txt_dir = tmp_path / "2026-01-02" / "txt"
        txt_dir.mkdir(parents=True)
        (txt_dir / "snapshot_1.txt").touch()
        (txt_dir / "readme.md").touch()
        (txt_dir / "image.jpg").touch()

        result = is_first_crawl_today(str(tmp_path), "2026-01-02")
        assert result is True  # Only 1 .txt file

    def test_first_crawl_multiple_txt_files(self, tmp_path):
        """测试多个txt文件"""
        txt_dir = tmp_path / "2026-01-02" / "txt"
        txt_dir.mkdir(parents=True)
        (txt_dir / "snapshot_1.txt").touch()
        (txt_dir / "snapshot_2.txt").touch()
        (txt_dir / "readme.md").touch()

        result = is_first_crawl_today(str(tmp_path), "2026-01-02")
        assert result is False  # 2 .txt files
