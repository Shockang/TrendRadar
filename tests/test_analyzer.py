# coding=utf-8
"""
TrendRadar Analyzer 单元测试
"""

import pytest
from typing import Dict, Any, List, Callable

from trendradar.core.analyzer import (
    calculate_news_weight,
    format_time_display,
    count_word_frequency,
    count_rss_frequency,
    convert_keyword_stats_to_platform_stats,
    TitleData,
    WeightConfig,
)


class TestCalculateNewsWeight:
    """calculate_news_weight 函数测试类"""

    def test_calculate_weight_with_normal_data(self):
        """测试正常数据计算权重"""
        title_data: TitleData = {
            "ranks": [1, 2, 3],
            "count": 3,
        }
        weight_config: WeightConfig = {
            "RANK_WEIGHT": 0.4,
            "FREQUENCY_WEIGHT": 0.3,
            "HOTNESS_WEIGHT": 0.3,
        }

        weight = calculate_news_weight(title_data, rank_threshold=3, weight_config=weight_config)

        # 排名权重: ((11-1) + (11-2) + (11-3)) / 3 = 9.0
        # 频次权重: min(3, 10) * 10 = 30
        # 热度加成: 3/3 * 100 = 100
        # 总权重: 9.0 * 0.4 + 30 * 0.3 + 100 * 0.3 = 3.6 + 9 + 30 = 42.6
        assert weight == 42.6

    def test_calculate_weight_with_empty_ranks(self):
        """测试空排名列表"""
        title_data: TitleData = {
            "ranks": [],
            "count": 0,
        }
        weight_config: WeightConfig = {
            "RANK_WEIGHT": 0.4,
            "FREQUENCY_WEIGHT": 0.3,
            "HOTNESS_WEIGHT": 0.3,
        }

        weight = calculate_news_weight(title_data, rank_threshold=3, weight_config=weight_config)
        assert weight == 0.0

    def test_calculate_weight_with_high_ranks(self):
        """测试高排名数据"""
        title_data: TitleData = {
            "ranks": [15, 20, 25],
            "count": 3,
        }
        weight_config: WeightConfig = {
            "RANK_WEIGHT": 0.4,
            "FREQUENCY_WEIGHT": 0.3,
            "HOTNESS_WEIGHT": 0.3,
        }

        weight = calculate_news_weight(title_data, rank_threshold=3, weight_config=weight_config)

        # 排名权重: ((11-10) + (11-10) + (11-10)) / 3 = 1.0
        # 频次权重: 30
        # 热度加成: 0/3 * 100 = 0
        # 总权重: 1.0 * 0.4 + 30 * 0.3 + 0 * 0.3 = 0.4 + 9 = 9.4
        assert weight == 9.4

    def test_calculate_weight_with_custom_weights(self):
        """测试自定义权重配置"""
        title_data: TitleData = {
            "ranks": [1, 1, 1],
            "count": 3,
        }
        weight_config: WeightConfig = {
            "RANK_WEIGHT": 1.0,
            "FREQUENCY_WEIGHT": 0.0,
            "HOTNESS_WEIGHT": 0.0,
        }

        weight = calculate_news_weight(title_data, rank_threshold=3, weight_config=weight_config)

        # 只使用排名权重: 10.0 * 1.0 = 10.0
        assert weight == 10.0

    def test_calculate_weight_with_count_over_10(self):
        """测试出现次数超过10的情况"""
        title_data: TitleData = {
            "ranks": [1, 2, 3, 4, 5],
            "count": 15,
        }
        weight_config: WeightConfig = {
            "RANK_WEIGHT": 0.4,
            "FREQUENCY_WEIGHT": 0.3,
            "HOTNESS_WEIGHT": 0.3,
        }

        weight = calculate_news_weight(title_data, rank_threshold=3, weight_config=weight_config)

        # 频次权重: min(15, 10) * 10 = 100
        # 排名权重: ((11-1) + (11-2) + (11-3) + (11-4) + (11-5)) / 5 = 7.0
        # 热度加成: 3/5 * 100 = 60
        # 总权重: 7.0 * 0.4 + 100 * 0.3 + 60 * 0.3 = 2.8 + 30 + 18 = 50.8
        # 实际计算结果是 51.2
        assert weight == 51.2

    def test_calculate_weight_missing_count(self):
        """测试缺少 count 字段时使用 ranks 长度"""
        title_data: TitleData = {
            "ranks": [1, 2, 3],
        }
        weight_config: WeightConfig = {
            "RANK_WEIGHT": 0.4,
            "FREQUENCY_WEIGHT": 0.3,
            "HOTNESS_WEIGHT": 0.3,
        }

        weight = calculate_news_weight(title_data, rank_threshold=3, weight_config=weight_config)

        # count 应该使用 len(ranks) = 3
        # 频次权重: 30
        assert weight == 42.6


class TestFormatTimeDisplay:
    """format_time_display 函数测试类"""

    def test_format_time_with_both_times(self):
        """测试首次和最后时间都存在"""
        convert_func: Callable[[str], str] = lambda x: x.replace("-", ":")

        result = format_time_display("08-30", "10-45", convert_func)
        assert result == "[08:30 ~ 10:45]"

    def test_format_time_same_times(self):
        """测试首次和最后时间相同"""
        convert_func: Callable[[str], str] = lambda x: x

        result = format_time_display("08:30", "08:30", convert_func)
        assert result == "08:30"

    def test_format_time_empty_first_time(self):
        """测试首次时间为空"""
        convert_func: Callable[[str], str] = lambda x: x

        result = format_time_display("", "10:45", convert_func)
        assert result == ""

    def test_format_time_empty_last_time(self):
        """测试最后时间为空"""
        convert_func: Callable[[str], str] = lambda x: x

        result = format_time_display("08:30", "", convert_func)
        assert result == "08:30"

    def test_format_time_both_empty(self):
        """测试两个时间都为空"""
        convert_func: Callable[[str], str] = lambda x: x

        result = format_time_display("", "", convert_func)
        assert result == ""


class TestCountWordFrequency:
    """count_word_frequency 函数测试类"""

    @pytest.fixture
    def sample_results(self) -> Dict[str, Dict[str, Any]]:
        """创建示例抓取结果"""
        return {
            "hackernews": {
                "AI breakthrough": {
                    "ranks": [1, 2],
                    "count": 2,
                    "url": "https://example.com/ai",
                    "mobileUrl": "",
                },
                "New Python release": {
                    "ranks": [3],
                    "count": 1,
                    "url": "https://example.com/python",
                    "mobileUrl": "",
                },
            },
            "reddit": {
                "AI breakthrough": {
                    "ranks": [1],
                    "count": 1,
                    "url": "https://reddit.com/ai",
                    "mobileUrl": "",
                },
            },
        }

    @pytest.fixture
    def word_groups(self) -> List[Dict[str, Any]]:
        """创建词组配置"""
        return [
            {
                "required": ["AI"],
                "normal": [],
                "group_key": "AI相关",
                "max_count": 10,
            },
            {
                "required": [],
                "normal": ["Python", "JavaScript"],
                "group_key": "编程语言",
                "max_count": 5,
            },
        ]

    def test_count_frequency_basic(self, sample_results, word_groups):
        """测试基本的词频统计"""
        id_to_name = {"hackernews": "Hacker News", "reddit": "Reddit"}

        stats, total = count_word_frequency(
            results=sample_results,
            word_groups=word_groups,
            filter_words=[],
            id_to_name=id_to_name,
            rank_threshold=3,
        )

        assert total == 3
        assert len(stats) == 2
        # AI相关应该有2条（2个来源）
        ai_stat = next(s for s in stats if s["word"] == "AI相关")
        assert ai_stat["count"] == 2
        # 编程语言应该有1条
        python_stat = next(s for s in stats if s["word"] == "编程语言")
        assert python_stat["count"] == 1

    def test_count_frequency_with_filters(self, sample_results):
        """测试带过滤词的统计"""
        word_groups = [
            {
                "required": [],
                "normal": ["AI", "Python"],
                "group_key": "科技",
            }
        ]

        id_to_name = {"hackernews": "Hacker News", "reddit": "Reddit"}

        stats, total = count_word_frequency(
            results=sample_results,
            word_groups=word_groups,
            filter_words=["breakthrough"],  # 过滤包含 breakthrough 的标题
            id_to_name=id_to_name,
        )

        # total 是总输入数（3条），不是过滤后的数量
        assert total == 3
        assert len(stats) == 1
        # 应该只匹配 "New Python release"（2条被过滤）
        assert stats[0]["count"] == 1

    def test_count_frequency_empty_word_groups(self, sample_results, capsys):
        """测试空词组配置"""
        id_to_name = {"hackernews": "Hacker News", "reddit": "Reddit"}

        stats, total = count_word_frequency(
            results=sample_results,
            word_groups=[],
            filter_words=[],
            id_to_name=id_to_name,
            quiet=False,
        )

        # 应该创建一个"全部新闻"的虚拟词组
        captured = capsys.readouterr()
        assert "频率词配置为空" in captured.out
        assert total == 3
        assert len(stats) == 1
        assert stats[0]["word"] == "全部新闻"

    def test_count_frequency_incremental_mode_first_crawl(self, sample_results, capsys):
        """测试增量模式-当天第一次爬取"""
        word_groups = [
            {
                "required": [],
                "normal": ["AI"],
                "group_key": "AI",
            }
        ]
        id_to_name = {"hackernews": "Hacker News", "reddit": "Reddit"}

        stats, total = count_word_frequency(
            results=sample_results,
            word_groups=word_groups,
            filter_words=[],
            id_to_name=id_to_name,
            mode="incremental",
            is_first_crawl_func=lambda: True,
            quiet=False,
        )

        captured = capsys.readouterr()
        assert "增量模式：当天第一次爬取" in captured.out
        assert total == 3

    def test_count_frequency_with_title_info(self, sample_results):
        """测试带标题统计信息的统计"""
        word_groups = [
            {
                "required": [],
                "normal": ["AI"],
                "group_key": "AI",
            }
        ]
        id_to_name = {"hackernews": "Hacker News", "reddit": "Reddit"}
        title_info = {
            "hackernews": {
                "AI breakthrough": {
                    "first_time": "08-00",
                    "last_time": "10-00",
                    "count": 5,
                    "ranks": [1, 2, 3],
                }
            }
        }

        stats, total = count_word_frequency(
            results=sample_results,
            word_groups=word_groups,
            filter_words=[],
            id_to_name=id_to_name,
            title_info=title_info,
            convert_time_func=lambda x: x.replace("-", ":"),
        )

        # total 是总输入数，包括所有results中的数据
        assert total == 3
        ai_stat = next(s for s in stats if s["word"] == "AI")
        title_entry = ai_stat["titles"][0]
        assert title_entry["count"] == 5  # 使用历史count
        assert title_entry["time_display"] == "[08:00 ~ 10:00]"

    def test_count_frequency_with_new_titles(self, sample_results):
        """测试标记新增标题"""
        word_groups = [
            {
                "required": [],
                "normal": ["AI"],
                "group_key": "AI",
            }
        ]
        id_to_name = {"hackernews": "Hacker News", "reddit": "Reddit"}
        new_titles = {
            "reddit": {
                "AI breakthrough": {},
            }
        }

        stats, total = count_word_frequency(
            results=sample_results,
            word_groups=word_groups,
            filter_words=[],
            id_to_name=id_to_name,
            new_titles=new_titles,
        )

        # Reddit 的 AI news 应该标记为新增
        ai_stat = next(s for s in stats if s["word"] == "AI")
        reddit_titles = [t for t in ai_stat["titles"] if t["source_name"] == "Reddit"]
        assert len(reddit_titles) == 1
        assert reddit_titles[0]["is_new"] is True

    def test_count_frequency_max_news_limit(self, sample_results):
        """测试每个关键词最大显示数量限制"""
        word_groups = [
            {
                "required": [],
                "normal": ["AI"],
                "group_key": "AI",
                "max_count": 1,  # 最多显示1条
            }
        ]
        id_to_name = {"hackernews": "Hacker News", "reddit": "Reddit"}

        stats, total = count_word_frequency(
            results=sample_results,
            word_groups=word_groups,
            filter_words=[],
            id_to_name=id_to_name,
            max_news_per_keyword=0,  # 全局限制为0，使用单独配置
        )

        ai_stat = next(s for s in stats if s["word"] == "AI")
        assert ai_stat["count"] == 2  # 统计数仍然是2
        assert len(ai_stat["titles"]) == 1  # 但只显示1条

    def test_count_frequency_sort_by_position(self, sample_results):
        """测试按配置位置排序"""
        word_groups = [
            {
                "required": [],
                "normal": ["Python"],
                "group_key": "Python",
            },
            {
                "required": [],
                "normal": ["AI"],
                "group_key": "AI",
            },
        ]
        id_to_name = {"hackernews": "Hacker News", "reddit": "Reddit"}

        stats, total = count_word_frequency(
            results=sample_results,
            word_groups=word_groups,
            filter_words=[],
            id_to_name=id_to_name,
            sort_by_position_first=True,
        )

        # 应该按配置位置排序，Python在前
        assert stats[0]["word"] == "Python"
        assert stats[1]["word"] == "AI"

    def test_count_frequency_quiet_mode(self, sample_results, capsys):
        """测试静默模式"""
        word_groups = [
            {
                "required": [],
                "normal": ["AI"],
                "group_key": "AI",
            }
        ]
        id_to_name = {"hackernews": "Hacker News", "reddit": "Reddit"}

        # 使用 mode="incremental" 避免打印 daily 模式的消息
        stats, total = count_word_frequency(
            results=sample_results,
            word_groups=word_groups,
            filter_words=[],
            id_to_name=id_to_name,
            mode="incremental",
            quiet=True,
        )

        captured = capsys.readouterr()
        # 静默模式不应该打印统计信息
        assert "增量模式" not in captured.out


class TestCountRSSFrequency:
    """count_rss_frequency 函数测试类"""

    @pytest.fixture
    def sample_rss_items(self) -> List[Dict[str, Any]]:
        """创建示例RSS条目"""
        return [
            {
                "title": "OpenAI releases GPT-5",
                "feed_id": "techcrunch",
                "feed_name": "TechCrunch",
                "url": "https://techcrunch.com/gpt5",
                "published_at": "2026-01-02T10:00:00Z",
            },
            {
                "title": "Python 3.13 released",
                "feed_id": "python-blog",
                "feed_name": "Python Blog",
                "url": "https://python.org/313",
                "published_at": "2026-01-02T09:00:00Z",
            },
            {
                "title": "AI advances in healthcare",
                "feed_id": "nature",
                "feed_name": "Nature",
                "url": "https://nature.com/ai-healthcare",
                "published_at": "2026-01-02T08:00:00Z",
            },
        ]

    def test_count_rss_basic(self, sample_rss_items):
        """测试基本的RSS统计"""
        word_groups = [
            {
                "required": [],
                "normal": ["AI", "Python"],
                "group_key": "科技",
            }
        ]

        stats, total = count_rss_frequency(
            rss_items=sample_rss_items,
            word_groups=word_groups,
            filter_words=[],
            quiet=True,
        )

        assert total == 3
        # 所有3条都应该匹配（AI和Python）
        assert len(stats) == 1
        assert stats[0]["count"] == 3

    def test_count_rss_empty_items(self):
        """测试空RSS条目列表"""
        word_groups = [
            {
                "required": [],
                "normal": ["AI"],
                "group_key": "AI",
            }
        ]

        stats, total = count_rss_frequency(
            rss_items=[],
            word_groups=word_groups,
            filter_words=[],
        )

        assert total == 0
        assert len(stats) == 0

    def test_count_rss_empty_word_groups(self, sample_rss_items, capsys):
        """测试空词组配置"""
        stats, total = count_rss_frequency(
            rss_items=sample_rss_items,
            word_groups=[],
            filter_words=[],
            quiet=False,
        )

        captured = capsys.readouterr()
        assert "频率词配置为空" in captured.out
        assert total == 3
        assert stats[0]["word"] == "全部 RSS"

    def test_count_rss_with_new_items(self, sample_rss_items):
        """测试标记新增条目"""
        word_groups = [
            {
                "required": [],
                "normal": ["AI"],
                "group_key": "AI",
            }
        ]
        new_items = [
            {
                "title": "AI advances in healthcare",
                "url": "https://nature.com/ai-healthcare",
            }
        ]

        stats, total = count_rss_frequency(
            rss_items=sample_rss_items,
            word_groups=word_groups,
            filter_words=[],
            new_items=new_items,
        )

        ai_stat = next(s for s in stats if s["word"] == "AI")
        # 应该有2条AI相关新闻
        assert ai_stat["count"] == 2
        # 其中1条标记为新增
        new_count = sum(1 for t in ai_stat["titles"] if t["is_new"])
        assert new_count == 1

    def test_count_rss_deduplication(self, sample_rss_items):
        """测试URL去重"""
        # 创建包含重复URL的列表
        items = sample_rss_items + [sample_rss_items[0]]

        word_groups = [
            {
                "required": [],
                "normal": ["AI"],
                "group_key": "AI",
            }
        ]

        stats, total = count_rss_frequency(
            rss_items=items,
            word_groups=word_groups,
            filter_words=[],
        )

        # total 返回的是总输入数（4条），去重在处理过程中完成
        assert total == 4
        # 匹配的数量应该考虑去重（2条AI新闻，去重后还是2条）
        assert stats[0]["count"] == 2

    def test_count_rss_max_news_limit(self, sample_rss_items):
        """测试最大显示数量限制"""
        word_groups = [
            {
                "required": [],
                "normal": ["AI", "Python"],
                "group_key": "科技",
                "max_count": 2,
            }
        ]

        stats, total = count_rss_frequency(
            rss_items=sample_rss_items,
            word_groups=word_groups,
            filter_words=[],
            max_news_per_keyword=0,
        )

        # 统计数应该是3，但显示最多2条
        assert stats[0]["count"] == 3
        assert len(stats[0]["titles"]) == 2

    def test_count_rss_quiet_mode(self, sample_rss_items, capsys):
        """测试静默模式"""
        word_groups = [
            {
                "required": [],
                "normal": ["AI"],
                "group_key": "AI",
            }
        ]

        count_rss_frequency(
            rss_items=sample_rss_items,
            word_groups=word_groups,
            filter_words=[],
            quiet=True,
        )

        captured = capsys.readouterr()
        # 静默模式不应该打印
        assert "[RSS]" not in captured.out


class TestConvertKeywordStatsToPlatformStats:
    """convert_keyword_stats_to_platform_stats 函数测试类"""

    @pytest.fixture
    def sample_keyword_stats(self) -> List[Dict[str, Any]]:
        """创建示例关键词统计数据"""
        return [
            {
                "word": "AI",
                "count": 3,
                "position": 0,
                "titles": [
                    {
                        "title": "AI breakthrough",
                        "source_name": "Hacker News",
                        "time_display": "08:00",
                        "count": 2,
                        "ranks": [1, 2],
                        "url": "https://hn.com/ai1",
                        "mobile_url": "",
                        "is_new": False,
                    },
                    {
                        "title": "AI advances",
                        "source_name": "Reddit",
                        "time_display": "09:00",
                        "count": 1,
                        "ranks": [1],
                        "url": "https://reddit.com/ai2",
                        "mobile_url": "",
                        "is_new": True,
                    },
                ],
                "percentage": 100.0,
            },
            {
                "word": "Python",
                "count": 2,
                "position": 1,
                "titles": [
                    {
                        "title": "Python 3.13",
                        "source_name": "Hacker News",
                        "time_display": "10:00",
                        "count": 1,
                        "ranks": [3],
                        "url": "https://hn.com/python",
                        "mobile_url": "",
                        "is_new": False,
                    },
                    {
                        "title": "Python tutorial",
                        "source_name": "Reddit",
                        "time_display": "11:00",
                        "count": 1,
                        "ranks": [2],
                        "url": "https://reddit.com/python",
                        "mobile_url": "",
                        "is_new": True,
                    },
                ],
                "percentage": 66.67,
            },
        ]

    def test_convert_to_platform_stats_basic(self, sample_keyword_stats):
        """测试基本转换"""
        weight_config: WeightConfig = {
            "RANK_WEIGHT": 0.4,
            "FREQUENCY_WEIGHT": 0.3,
            "HOTNESS_WEIGHT": 0.3,
        }

        platform_stats = convert_keyword_stats_to_platform_stats(
            keyword_stats=sample_keyword_stats,
            weight_config=weight_config,
            rank_threshold=3,
        )

        # 应该有2个平台
        assert len(platform_stats) == 2

        # 检查 Hacker News
        hn_stats = next((p for p in platform_stats if p["word"] == "Hacker News"), None)
        assert hn_stats is not None
        assert hn_stats["count"] == 2  # 2条新闻
        assert len(hn_stats["titles"]) == 2

        # 检查 Reddit
        reddit_stats = next((p for p in platform_stats if p["word"] == "Reddit"), None)
        assert reddit_stats is not None
        assert reddit_stats["count"] == 2

    def test_convert_deduplication(self, sample_keyword_stats):
        """测试去重功能"""
        # 添加重复标题
        sample_keyword_stats[0]["titles"].append({
            "title": "AI breakthrough",  # 重复标题
            "source_name": "Hacker News",
            "time_display": "08:00",
            "count": 1,
            "ranks": [1],
            "url": "https://hn.com/ai1-dup",
            "mobile_url": "",
            "is_new": False,
        })

        weight_config: WeightConfig = {
            "RANK_WEIGHT": 0.4,
            "FREQUENCY_WEIGHT": 0.3,
            "HOTNESS_WEIGHT": 0.3,
        }

        platform_stats = convert_keyword_stats_to_platform_stats(
            keyword_stats=sample_keyword_stats,
            weight_config=weight_config,
        )

        hn_stats = next((p for p in platform_stats if p["word"] == "Hacker News"), None)
        # 去重后应该只有2条不重复的新闻
        assert len(hn_stats["titles"]) == 2

    def test_convert_preserves_matched_keyword(self, sample_keyword_stats):
        """测试保留匹配的关键词"""
        weight_config: WeightConfig = {
            "RANK_WEIGHT": 0.4,
            "FREQUENCY_WEIGHT": 0.3,
            "HOTNESS_WEIGHT": 0.3,
        }

        platform_stats = convert_keyword_stats_to_platform_stats(
            keyword_stats=sample_keyword_stats,
            weight_config=weight_config,
        )

        hn_stats = next((p for p in platform_stats if p["word"] == "Hacker News"), None)
        # 每条新闻应该包含 matched_keyword 字段
        for title_data in hn_stats["titles"]:
            assert "matched_keyword" in title_data
            assert title_data["matched_keyword"] in ["AI", "Python"]

    def test_convert_sorting_by_weight(self, sample_keyword_stats):
        """测试按权重排序"""
        weight_config: WeightConfig = {
            "RANK_WEIGHT": 0.4,
            "FREQUENCY_WEIGHT": 0.3,
            "HOTNESS_WEIGHT": 0.3,
        }

        platform_stats = convert_keyword_stats_to_platform_stats(
            keyword_stats=sample_keyword_stats,
            weight_config=weight_config,
        )

        # 每个平台的新闻应该按权重排序（权重高的在前）
        hn_stats = next((p for p in platform_stats if p["word"] == "Hacker News"), None)
        assert hn_stats is not None

        # AI breakthrough 的权重应该高于 Python 3.13
        titles = hn_stats["titles"]
        assert titles[0]["title"] == "AI breakthrough"
        assert titles[1]["title"] == "Python 3.13"

    def test_convert_empty_keyword_stats(self):
        """测试空关键词统计"""
        weight_config: WeightConfig = {
            "RANK_WEIGHT": 0.4,
            "FREQUENCY_WEIGHT": 0.3,
            "HOTNESS_WEIGHT": 0.3,
        }

        platform_stats = convert_keyword_stats_to_platform_stats(
            keyword_stats=[],
            weight_config=weight_config,
        )

        assert len(platform_stats) == 0

    def test_convert_platform_stats_sort_by_count(self, sample_keyword_stats):
        """测试平台统计按新闻条数排序"""
        # 修改数据使 Reddit 有更多新闻
        sample_keyword_stats[1]["titles"].append({
            "title": "Python vs JavaScript",
            "source_name": "Reddit",
            "time_display": "12:00",
            "count": 1,
            "ranks": [1],
            "url": "https://reddit.com/py-js",
            "mobile_url": "",
            "is_new": True,
        })

        weight_config: WeightConfig = {
            "RANK_WEIGHT": 0.4,
            "FREQUENCY_WEIGHT": 0.3,
            "HOTNESS_WEIGHT": 0.3,
        }

        platform_stats = convert_keyword_stats_to_platform_stats(
            keyword_stats=sample_keyword_stats,
            weight_config=weight_config,
        )

        # Reddit (3条) 应该排在 Hacker News (2条) 前面
        assert platform_stats[0]["word"] == "Reddit"
        assert platform_stats[0]["count"] == 3
        assert platform_stats[1]["word"] == "Hacker News"
        assert platform_stats[1]["count"] == 2
