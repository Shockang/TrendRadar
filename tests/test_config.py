# coding=utf-8
"""
TrendRadar core/config.py 单元测试
"""

import pytest
from io import StringIO
import sys

from trendradar.core.config import (
    parse_multi_account_config,
    validate_paired_configs,
    limit_accounts,
    get_account_at_index,
)


class TestParseMultiAccountConfig:
    """parse_multi_account_config 函数测试类"""

    def test_parse_single_account(self):
        """测试解析单个账号"""
        result = parse_multi_account_config("url1")
        assert result == ["url1"]

    def test_parse_multiple_accounts(self):
        """测试解析多个账号"""
        result = parse_multi_account_config("url1;url2;url3")
        assert result == ["url1", "url2", "url3"]

    def test_parse_with_spaces(self):
        """测试带空格的账号解析"""
        result = parse_multi_account_config("url1 ; url2 ; url3")
        assert result == ["url1", "url2", "url3"]

    def test_parse_with_empty_first(self):
        """测试第一个账号为空"""
        result = parse_multi_account_config(";url2;url3")
        assert result == ["", "url2", "url3"]

    def test_parse_with_empty_middle(self):
        """测试中间账号为空"""
        result = parse_multi_account_config("url1;;url3")
        assert result == ["url1", "", "url3"]

    def test_parse_with_empty_last(self):
        """测试最后一个账号为空"""
        result = parse_multi_account_config("url1;url2;")
        assert result == ["url1", "url2", ""]

    def test_parse_empty_string(self):
        """测试空字符串"""
        result = parse_multi_account_config("")
        assert result == []

    def test_parse_only_separators(self):
        """测试只有分隔符"""
        result = parse_multi_account_config(";;;")
        assert result == []

    def test_parse_custom_separator(self):
        """测试自定义分隔符"""
        result = parse_multi_account_config("url1,url2,url3", separator=",")
        assert result == ["url1", "url2", "url3"]

    def test_parse_none_value(self):
        """测试None值"""
        result = parse_multi_account_config(None)  # type: ignore
        assert result == []

    def test_parse_with_duplicate_separators(self):
        """测试连续分隔符"""
        result = parse_multi_account_config("url1;;url2;;;url3")
        assert result == ["url1", "", "url2", "", "", "url3"]


class TestValidatePairedConfigs:
    """validate_paired_configs 函数测试类"""

    def test_validate_empty_configs(self):
        """测试空配置"""
        is_valid, count = validate_paired_configs({}, "TestChannel")
        assert is_valid is True
        assert count == 0

    def test_validate_all_empty_lists(self):
        """测试所有配置都为空列表"""
        configs = {
            "token": [],
            "chat_id": [],
        }
        is_valid, count = validate_paired_configs(configs, "Telegram")
        assert is_valid is True
        assert count == 0

    def test_validate_single_config(self):
        """测试单个配置"""
        configs = {
            "token": ["t1", "t2"],
        }
        is_valid, count = validate_paired_configs(configs, "Telegram")
        assert is_valid is True
        assert count == 2

    def test_validate_matching_configs(self):
        """测试配置数量匹配"""
        configs = {
            "token": ["t1", "t2"],
            "chat_id": ["c1", "c2"]
        }
        is_valid, count = validate_paired_configs(configs, "Telegram")
        assert is_valid is True
        assert count == 2

    def test_validate_mismatching_configs(self):
        """测试配置数量不匹配"""
        configs = {
            "token": ["t1", "t2"],
            "chat_id": ["c1"]
        }

        # 捕获打印输出
        captured_output = StringIO()
        sys.stdout = captured_output

        is_valid, count = validate_paired_configs(configs, "Telegram")

        sys.stdout = sys.__stdout__

        assert is_valid is False
        assert count == 0
        output = captured_output.getvalue()
        assert "Telegram 配置错误" in output
        assert "配对配置数量不一致" in output

    def test_validate_with_required_keys_present(self):
        """测试必须项存在"""
        configs = {
            "token": ["t1", "t2"],
            "chat_id": ["c1", "c2"]
        }
        is_valid, count = validate_paired_configs(
            configs, "Telegram", required_keys=["token", "chat_id"]
        )
        assert is_valid is True
        assert count == 2

    def test_validate_with_required_keys_missing(self):
        """测试必须项缺失"""
        configs = {
            "token": ["t1", "t2"],
        }
        is_valid, count = validate_paired_configs(
            configs, "Telegram", required_keys=["token", "chat_id"]
        )
        # 必须项缺失，视为未配置
        assert is_valid is True
        assert count == 0

    def test_validate_with_required_keys_empty(self):
        """测试必须项为空"""
        configs = {
            "token": [],
            "chat_id": []
        }
        is_valid, count = validate_paired_configs(
            configs, "Telegram", required_keys=["token", "chat_id"]
        )
        assert is_valid is True
        assert count == 0

    def test_validate_three_configs_matching(self):
        """测试三个配置匹配"""
        configs = {
            "token": ["t1", "t2", "t3"],
            "chat_id": ["c1", "c2", "c3"],
            "secret": ["s1", "s2", "s3"]
        }
        is_valid, count = validate_paired_configs(configs, "TestChannel")
        assert is_valid is True
        assert count == 3

    def test_validate_partial_empty_configs(self):
        """测试部分配置为空"""
        configs = {
            "token": ["t1", "t2"],
            "chat_id": ["c1", "c2"],
            "optional": []
        }
        is_valid, count = validate_paired_configs(configs, "Telegram")
        assert is_valid is True
        assert count == 2


class TestLimitAccounts:
    """limit_accounts 函数测试类"""

    def test_limit_accounts_within_limit(self):
        """测试账号数在限制内"""
        accounts = ["a1", "a2", "a3"]
        result = limit_accounts(accounts, 5, "飞书")
        assert result == ["a1", "a2", "a3"]

    def test_limit_accounts_equal_to_limit(self):
        """测试账号数等于限制"""
        accounts = ["a1", "a2", "a3"]
        result = limit_accounts(accounts, 3, "飞书")
        assert result == ["a1", "a2", "a3"]

    def test_limit_accounts_exceeds_limit(self):
        """测试账号数超过限制"""
        accounts = ["a1", "a2", "a3"]
        captured_output = StringIO()
        sys.stdout = captured_output

        result = limit_accounts(accounts, 2, "飞书")

        sys.stdout = sys.__stdout__

        assert result == ["a1", "a2"]
        output = captured_output.getvalue()
        assert "飞书 配置了 3 个账号" in output
        assert "超过最大限制 2" in output
        assert "GitHub Actions" in output

    def test_limit_accounts_empty_list(self):
        """测试空账号列表"""
        accounts = []
        result = limit_accounts(accounts, 5, "飞书")
        assert result == []

    def test_limit_accounts_single_account(self):
        """测试单个账号"""
        accounts = ["a1"]
        result = limit_accounts(accounts, 1, "飞书")
        assert result == ["a1"]

    def test_limit_accounts_max_is_zero(self):
        """测试最大限制为0"""
        accounts = ["a1", "a2", "a3"]
        result = limit_accounts(accounts, 0, "飞书")
        assert result == []

    def test_limit_accounts_large_difference(self):
        """测试账号数远超限制"""
        accounts = [f"a{i}" for i in range(100)]
        captured_output = StringIO()
        sys.stdout = captured_output

        result = limit_accounts(accounts, 10, "钉钉")

        sys.stdout = sys.__stdout__

        assert len(result) == 10
        assert result == [f"a{i}" for i in range(10)]


class TestGetAccountAtIndex:
    """get_account_at_index 函数测试类"""

    def test_get_account_at_valid_index(self):
        """测试有效索引"""
        accounts = ["a", "b", "c"]
        result = get_account_at_index(accounts, 1)
        assert result == "b"

    def test_get_account_at_first_index(self):
        """测试第一个索引"""
        accounts = ["a", "b", "c"]
        result = get_account_at_index(accounts, 0)
        assert result == "a"

    def test_get_account_at_last_index(self):
        """测试最后一个索引"""
        accounts = ["a", "b", "c"]
        result = get_account_at_index(accounts, 2)
        assert result == "c"

    def test_get_account_at_out_of_range(self):
        """测试索引超出范围"""
        accounts = ["a", "b", "c"]
        result = get_account_at_index(accounts, 5)
        assert result == ""

    def test_get_account_at_out_of_range_with_default(self):
        """测试索引超出范围，使用默认值"""
        accounts = ["a", "b", "c"]
        result = get_account_at_index(accounts, 5, default="default_value")
        assert result == "default_value"

    def test_get_account_at_empty_value(self):
        """测试账号值为空"""
        accounts = ["a", "", "c"]
        result = get_account_at_index(accounts, 1)
        assert result == ""

    def test_get_account_at_empty_value_with_default(self):
        """测试账号值为空，使用默认值"""
        accounts = ["a", "", "c"]
        result = get_account_at_index(accounts, 1, default="default")
        assert result == "default"

    def test_get_account_at_negative_index(self):
        """测试负索引（Python负索引会从末尾计数）"""
        accounts = ["a", "b", "c"]
        result = get_account_at_index(accounts, -1)
        # Python的负索引会从列表末尾计数，所以-1会返回最后一个元素
        assert result == "c"

    def test_get_account_at_empty_list(self):
        """测试空列表"""
        accounts = []
        result = get_account_at_index(accounts, 0)
        assert result == ""

    def test_get_account_at_index_with_spaces(self):
        """测试账号值带空格"""
        accounts = ["a", " b ", "c"]
        result = get_account_at_index(accounts, 1)
        assert result == " b "


class TestConfigIntegration:
    """配置模块集成测试类"""

    def test_parse_and_validate_workflow(self):
        """测试解析和验证工作流"""
        # 模拟多账号配置
        tokens = parse_multi_account_config("t1;t2;t3")
        chat_ids = parse_multi_account_config("c1;c2;c3")

        configs = {
            "token": tokens,
            "chat_id": chat_ids
        }

        is_valid, count = validate_paired_configs(configs, "Telegram")
        assert is_valid is True
        assert count == 3

    def test_parse_validate_and_limit_workflow(self):
        """测试解析、验证和限制工作流"""
        # 解析配置
        webhooks = parse_multi_account_config("w1;w2;w3;w4;w5")

        # 限制账号数量
        limited = limit_accounts(webhooks, 3, "飞书")

        assert len(limited) == 3
        assert limited == ["w1", "w2", "w3"]

    def test_get_accounts_safely_workflow(self):
        """测试安全获取账号工作流"""
        tokens = parse_multi_account_config("t1;t2;t3")
        chat_ids = parse_multi_account_config("c1;c2;c3")

        configs = {
            "token": tokens,
            "chat_id": chat_ids
        }

        is_valid, count = validate_paired_configs(configs, "Telegram")
        assert is_valid is True

        # 安全获取每个账号的配置
        for i in range(count):
            token = get_account_at_index(tokens, i)
            chat_id = get_account_at_index(chat_ids, i)
            assert token != ""
            assert chat_id != ""
