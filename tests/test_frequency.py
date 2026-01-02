# coding=utf-8
"""
TrendRadar Core Frequency 模块单元测试
"""

import pytest
import tempfile
import os
from pathlib import Path

from trendradar.core.frequency import load_frequency_words, matches_word_groups


class TestLoadFrequencyWords:
    """load_frequency_words 函数测试类"""

    def test_load_basic_word_groups(self):
        """测试加载基本词组"""
        content = """
人工智能

机器学习

深度学习
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            f.flush()
            temp_path = f.name

        try:
            word_groups, filter_words, global_filters = load_frequency_words(temp_path)

            # 应该有3个词组（每个词都是单独一组）
            assert len(word_groups) == 3

            # 第一个词组
            assert word_groups[0]["group_key"] == "人工智能"
            assert word_groups[0]["normal"] == ["人工智能"]
            assert word_groups[0]["required"] == []

            # 没有过滤词
            assert len(filter_words) == 0
            assert len(global_filters) == 0
        finally:
            os.unlink(temp_path)

    def test_load_with_required_words(self):
        """测试加载必须词（+前缀）"""
        content = """
+人工智能
+机器学习
深度学习
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            f.flush()
            temp_path = f.name

        try:
            word_groups, filter_words, global_filters = load_frequency_words(temp_path)

            assert len(word_groups) == 1
            assert word_groups[0]["required"] == ["人工智能", "机器学习"]
            assert word_groups[0]["normal"] == ["深度学习"]
            assert word_groups[0]["group_key"] == "深度学习"  # 只有普通词作为key
        finally:
            os.unlink(temp_path)

    def test_load_with_filter_words(self):
        """测试加载过滤词（!前缀）"""
        content = """
人工智能
!广告
!推广
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            f.flush()
            temp_path = f.name

        try:
            word_groups, filter_words, global_filters = load_frequency_words(temp_path)

            assert len(word_groups) == 1
            assert word_groups[0]["normal"] == ["人工智能"]
            assert "广告" in filter_words
            assert "推广" in filter_words
        finally:
            os.unlink(temp_path)

    def test_load_with_max_count(self):
        """测试加载最大显示数量（@前缀）"""
        content = """
人工智能
@10
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            f.flush()
            temp_path = f.name

        try:
            word_groups, filter_words, global_filters = load_frequency_words(temp_path)

            assert len(word_groups) == 1
            assert word_groups[0]["max_count"] == 10
        finally:
            os.unlink(temp_path)

    def test_load_with_invalid_max_count(self):
        """测试无效的最大显示数量"""
        content = """
人工智能
@abc
@-5
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            f.flush()
            temp_path = f.name

        try:
            word_groups, filter_words, global_filters = load_frequency_words(temp_path)

            # 无效的max_count应该被忽略，保持默认值0
            assert word_groups[0]["max_count"] == 0
        finally:
            os.unlink(temp_path)

    def test_load_with_global_filters(self):
        """测试加载全局过滤词"""
        content = """
[GLOBAL_FILTER]
广告
推广
营销

[WORD_GROUPS]
人工智能
机器学习
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            f.flush()
            temp_path = f.name

        try:
            word_groups, filter_words, global_filters = load_frequency_words(temp_path)

            assert len(global_filters) == 3
            assert "广告" in global_filters
            assert "推广" in global_filters
            assert "营销" in global_filters

            # 词组应该正常加载
            assert len(word_groups) == 1
        finally:
            os.unlink(temp_path)

    def test_load_with_sections(self):
        """测试带区域标记的配置文件"""
        content = """
[WORD_GROUPS]
人工智能
+机器学习

大数据
@5

[GLOBAL_FILTER]
广告
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            f.flush()
            temp_path = f.name

        try:
            word_groups, filter_words, global_filters = load_frequency_words(temp_path)

            # 应该有2个词组
            assert len(word_groups) == 2
            assert len(global_filters) == 1
        finally:
            os.unlink(temp_path)

    def test_load_empty_file(self):
        """测试加载空文件"""
        content = ""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            f.flush()
            temp_path = f.name

        try:
            word_groups, filter_words, global_filters = load_frequency_words(temp_path)

            assert len(word_groups) == 0
            assert len(filter_words) == 0
            assert len(global_filters) == 0
        finally:
            os.unlink(temp_path)

    def test_load_file_not_found(self):
        """测试文件不存在的异常"""
        with pytest.raises(FileNotFoundError):
            load_frequency_words("/nonexistent/file.txt")

    def test_load_with_env_variable(self):
        """测试从环境变量读取路径"""
        content = "测试词组"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            f.flush()
            temp_path = f.name

        try:
            # 设置环境变量
            os.environ["FREQUENCY_WORDS_PATH"] = temp_path
            word_groups, filter_words, global_filters = load_frequency_words()

            assert len(word_groups) == 1
        finally:
            os.unlink(temp_path)
            del os.environ["FREQUENCY_WORDS_PATH"]

    def test_load_complex_word_group(self):
        """测试复杂词组组合"""
        content = """
+人工智能
+机器学习
深度学习
!广告
@10
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            f.flush()
            temp_path = f.name

        try:
            word_groups, filter_words, global_filters = load_frequency_words(temp_path)

            assert len(word_groups) == 1
            assert set(word_groups[0]["required"]) == {"人工智能", "机器学习"}
            assert word_groups[0]["normal"] == ["深度学习"]
            assert word_groups[0]["max_count"] == 10
            assert "广告" in filter_words
        finally:
            os.unlink(temp_path)


class TestMatchesWordGroups:
    """matches_word_groups 函数测试类"""

    def test_match_normal_word(self):
        """测试匹配普通词"""
        word_groups = [
            {"group_key": "人工智能", "normal": ["人工智能"], "required": [], "max_count": 0}
        ]
        filter_words = []
        global_filters = []

        assert matches_word_groups("人工智能发展迅速", word_groups, filter_words, global_filters) is True
        assert matches_word_groups("机器学习很重要", word_groups, filter_words, global_filters) is False

    def test_match_required_words(self):
        """测试匹配必须词"""
        word_groups = [
            {
                "group_key": "深度学习",
                "normal": ["深度学习"],
                "required": ["人工智能", "机器学习"],
                "max_count": 0
            }
        ]
        filter_words = []
        global_filters = []

        # 必须同时包含所有必须词
        assert matches_word_groups("人工智能和机器学习推动了深度学习发展", word_groups, filter_words, global_filters) is True
        assert matches_word_groups("人工智能发展迅速", word_groups, filter_words, global_filters) is False
        assert matches_word_groups("深度学习很重要", word_groups, filter_words, global_filters) is False

    def test_match_with_filter_words(self):
        """测试过滤词"""
        word_groups = [
            {"group_key": "人工智能", "normal": ["人工智能"], "required": [], "max_count": 0}
        ]
        filter_words = ["广告", "推广"]
        global_filters = []

        # 包含过滤词应该被排除
        assert matches_word_groups("人工智能广告推广", word_groups, filter_words, global_filters) is False
        assert matches_word_groups("人工智能发展迅速", word_groups, filter_words, global_filters) is True

    def test_match_with_global_filters(self):
        """测试全局过滤词"""
        word_groups = [
            {"group_key": "人工智能", "normal": ["人工智能"], "required": [], "max_count": 0}
        ]
        filter_words = []
        global_filters = ["广告", "推广"]

        # 全局过滤词应该优先级最高
        assert matches_word_groups("人工智能广告推广", word_groups, filter_words, global_filters) is False
        assert matches_word_groups("人工智能发展迅速", word_groups, filter_words, global_filters) is True

    def test_match_empty_word_groups(self):
        """测试空词组列表（匹配所有）"""
        word_groups = []
        filter_words = []
        global_filters = []

        # 没有配置词组时，应该匹配所有标题
        assert matches_word_groups("任意标题", word_groups, filter_words, global_filters) is True
        assert matches_word_groups("另一个标题", word_groups, filter_words, global_filters) is True

    def test_match_empty_title(self):
        """测试空标题"""
        word_groups = [
            {"group_key": "人工智能", "normal": ["人工智能"], "required": [], "max_count": 0}
        ]
        filter_words = []
        global_filters = []

        assert matches_word_groups("", word_groups, filter_words, global_filters) is False
        assert matches_word_groups("   ", word_groups, filter_words, global_filters) is False

    def test_match_case_insensitive(self):
        """测试大小写不敏感"""
        word_groups = [
            {"group_key": "AI", "normal": ["ai"], "required": [], "max_count": 0}
        ]
        filter_words = ["ad"]
        global_filters = []

        assert matches_word_groups("AI技术发展", word_groups, filter_words, global_filters) is True
        assert matches_word_groups("ai技术发展", word_groups, filter_words, global_filters) is True
        assert matches_word_groups("This is an AD", word_groups, filter_words, global_filters) is False

    def test_match_multiple_groups(self):
        """测试多个词组"""
        word_groups = [
            {"group_key": "人工智能", "normal": ["人工智能"], "required": [], "max_count": 0},
            {"group_key": "区块链", "normal": ["区块链"], "required": [], "max_count": 0}
        ]
        filter_words = []
        global_filters = []

        # 匹配任意一个词组即可
        assert matches_word_groups("人工智能发展", word_groups, filter_words, global_filters) is True
        assert matches_word_groups("区块链技术", word_groups, filter_words, global_filters) is True
        assert matches_word_groups("大数据分析", word_groups, filter_words, global_filters) is False

    def test_match_none_title(self):
        """测试 None 标题"""
        word_groups = [
            {"group_key": "人工智能", "normal": ["人工智能"], "required": [], "max_count": 0}
        ]
        filter_words = []
        global_filters = []

        # None 应该被转换为空字符串
        assert matches_word_groups(None, word_groups, filter_words, global_filters) is False

    def test_match_non_string_title(self):
        """测试非字符串标题"""
        word_groups = [
            {"group_key": "number", "normal": ["123"], "required": [], "max_count": 0}
        ]
        filter_words = []
        global_filters = []

        # 非字符串应该被转换为字符串
        assert matches_word_groups(123, word_groups, filter_words, global_filters) is True
        assert matches_word_groups(True, word_groups, filter_words, global_filters) is False

    def test_global_filters_with_special_prefix(self):
        """测试全局过滤区忽略特殊前缀"""
        content = """
[GLOBAL_FILTER]
广告
!not_filter
+not_filter
@not_filter

[WORD_GROUPS]
人工智能
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            f.flush()
            temp_path = f.name

        try:
            word_groups, filter_words, global_filters = load_frequency_words(temp_path)

            # 全局过滤区应该只包含纯文本，忽略特殊前缀
            assert len(global_filters) == 1
            assert "广告" in global_filters
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
