# coding=utf-8
"""
测试 core/loader.py 模块的配置加载功能
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, Any

import pytest
import yaml

from trendradar.core.loader import (
    _get_env_bool,
    _get_env_int,
    _get_env_str,
    _load_app_config,
    _load_crawler_config,
    _load_report_config,
    _load_notification_config,
    _load_push_window_config,
    _load_weight_config,
    _load_rss_config,
    _load_storage_config,
    _load_webhook_config,
    _print_notification_sources,
    load_config,
)


class TestGetEnvBool:
    """测试环境变量布尔值获取"""

    def test_get_env_bool_true(self) -> None:
        """测试获取true值"""
        os.environ["TEST_BOOL"] = "true"
        assert _get_env_bool("TEST_BOOL") is True
        del os.environ["TEST_BOOL"]

    def test_get_env_bool_false(self) -> None:
        """测试获取false值"""
        os.environ["TEST_BOOL"] = "false"
        assert _get_env_bool("TEST_BOOL") is False
        del os.environ["TEST_BOOL"]

    def test_get_env_bool_one(self) -> None:
        """测试获取1值"""
        os.environ["TEST_BOOL"] = "1"
        assert _get_env_bool("TEST_BOOL") is True
        del os.environ["TEST_BOOL"]

    def test_get_env_bool_zero(self) -> None:
        """测试获取0值"""
        os.environ["TEST_BOOL"] = "0"
        assert _get_env_bool("TEST_BOOL") is False
        del os.environ["TEST_BOOL"]

    def test_get_env_bool_case_insensitive(self) -> None:
        """测试大小写不敏感"""
        os.environ["TEST_BOOL"] = "TRUE"
        assert _get_env_bool("TEST_BOOL") is True
        del os.environ["TEST_BOOL"]

    def test_get_env_bool_empty(self) -> None:
        """测试空值返回None"""
        assert _get_env_bool("NONEXISTENT_BOOL") is None

    def test_get_env_bool_whitespace(self) -> None:
        """测试带空格的值"""
        os.environ["TEST_BOOL"] = "  true  "
        assert _get_env_bool("TEST_BOOL") is True
        del os.environ["TEST_BOOL"]


class TestGetEnvInt:
    """测试环境变量整数值获取"""

    def test_get_env_int_valid(self) -> None:
        """测试获取有效整数"""
        os.environ["TEST_INT"] = "42"
        assert _get_env_int("TEST_INT") == 42
        del os.environ["TEST_INT"]

    def test_get_env_int_default(self) -> None:
        """测试默认值"""
        assert _get_env_int("NONEXISTENT_INT", 10) == 10

    def test_get_env_int_invalid(self) -> None:
        """测试无效值返回默认值"""
        os.environ["TEST_INT"] = "invalid"
        assert _get_env_int("TEST_INT", 10) == 10
        del os.environ["TEST_INT"]

    def test_get_env_int_whitespace(self) -> None:
        """测试带空格的值"""
        os.environ["TEST_INT"] = "  42  "
        assert _get_env_int("TEST_INT") == 42
        del os.environ["TEST_INT"]


class TestGetEnvStr:
    """测试环境变量字符串值获取"""

    def test_get_env_str_valid(self) -> None:
        """测试获取有效字符串"""
        os.environ["TEST_STR"] = "test_value"
        assert _get_env_str("TEST_STR") == "test_value"
        del os.environ["TEST_STR"]

    def test_get_env_str_default(self) -> None:
        """测试默认值"""
        assert _get_env_str("NONEXISTENT_STR", "default") == "default"

    def test_get_env_str_whitespace(self) -> None:
        """测试自动去除空格"""
        os.environ["TEST_STR"] = "  test  "
        assert _get_env_str("TEST_STR") == "test"
        del os.environ["TEST_STR"]


class TestLoadAppConfig:
    """测试应用配置加载"""

    def test_load_app_config_basic(self) -> None:
        """测试基本应用配置"""
        config_data = {
            "app": {"show_version_update": False, "timezone": "UTC"},
            "advanced": {"version_check_url": "http://example.com"}
        }
        result = _load_app_config(config_data)
        assert result["SHOW_VERSION_UPDATE"] is False
        assert result["TIMEZONE"] == "UTC"
        assert result["VERSION_CHECK_URL"] == "http://example.com"

    def test_load_app_config_defaults(self) -> None:
        """测试默认值"""
        config_data = {}
        result = _load_app_config(config_data)
        assert result["SHOW_VERSION_UPDATE"] is True
        assert result["TIMEZONE"] == "Asia/Shanghai"
        assert result["VERSION_CHECK_URL"] == ""

    def test_load_app_config_env_override(self) -> None:
        """测试环境变量覆盖"""
        os.environ["TIMEZONE"] = "America/New_York"
        config_data = {"app": {"timezone": "UTC"}}
        result = _load_app_config(config_data)
        assert result["TIMEZONE"] == "America/New_York"
        del os.environ["TIMEZONE"]


class TestLoadCrawlerConfig:
    """测试爬虫配置加载"""

    def test_load_crawler_config_basic(self) -> None:
        """测试基本爬虫配置"""
        config_data = {
            "advanced": {
                "crawler": {
                    "request_interval": 200,
                    "use_proxy": True,
                    "default_proxy": "http://proxy",
                    "enabled": False
                }
            }
        }
        result = _load_crawler_config(config_data)
        assert result["REQUEST_INTERVAL"] == 200
        assert result["USE_PROXY"] is True
        assert result["DEFAULT_PROXY"] == "http://proxy"
        assert result["ENABLE_CRAWLER"] is False

    def test_load_crawler_config_defaults(self) -> None:
        """测试默认值"""
        config_data = {}
        result = _load_crawler_config(config_data)
        assert result["REQUEST_INTERVAL"] == 100
        assert result["USE_PROXY"] is False
        assert result["DEFAULT_PROXY"] == ""
        assert result["ENABLE_CRAWLER"] is True

    def test_load_crawler_config_env_override(self) -> None:
        """测试环境变量覆盖"""
        os.environ["ENABLE_CRAWLER"] = "false"
        config_data = {"advanced": {"crawler": {"enabled": True}}}
        result = _load_crawler_config(config_data)
        assert result["ENABLE_CRAWLER"] is False
        del os.environ["ENABLE_CRAWLER"]


class TestLoadReportConfig:
    """测试报告配置加载"""

    def test_load_report_config_basic(self) -> None:
        """测试基本报告配置"""
        config_data = {
            "report": {
                "mode": "realtime",
                "display_mode": "platform",
                "rank_threshold": 20,
                "sort_by_position_first": True,
                "max_news_per_keyword": 50,
                "reverse_content_order": True
            }
        }
        result = _load_report_config(config_data)
        assert result["REPORT_MODE"] == "realtime"
        assert result["DISPLAY_MODE"] == "platform"
        assert result["RANK_THRESHOLD"] == 20
        assert result["SORT_BY_POSITION_FIRST"] is True
        assert result["MAX_NEWS_PER_KEYWORD"] == 50
        assert result["REVERSE_CONTENT_ORDER"] is True

    def test_load_report_config_defaults(self) -> None:
        """测试默认值"""
        config_data = {}
        result = _load_report_config(config_data)
        assert result["REPORT_MODE"] == "daily"
        assert result["DISPLAY_MODE"] == "keyword"
        assert result["RANK_THRESHOLD"] == 10
        assert result["SORT_BY_POSITION_FIRST"] is False
        assert result["MAX_NEWS_PER_KEYWORD"] == 0
        assert result["REVERSE_CONTENT_ORDER"] is False

    def test_load_report_config_env_override(self) -> None:
        """测试环境变量覆盖"""
        os.environ["REPORT_MODE"] = "realtime"
        os.environ["SORT_BY_POSITION_FIRST"] = "true"
        config_data = {"report": {"mode": "daily"}}
        result = _load_report_config(config_data)
        assert result["REPORT_MODE"] == "realtime"
        assert result["SORT_BY_POSITION_FIRST"] is True
        del os.environ["REPORT_MODE"]
        del os.environ["SORT_BY_POSITION_FIRST"]


class TestLoadNotificationConfig:
    """测试通知配置加载"""

    def test_load_notification_config_basic(self) -> None:
        """测试基本通知配置"""
        config_data = {
            "notification": {"enabled": False},
            "advanced": {
                "batch_size": {
                    "default": 2000,
                    "dingtalk": 10000,
                    "feishu": 15000,
                    "bark": 1800,
                    "slack": 2000
                },
                "batch_send_interval": 2.0,
                "feishu_message_separator": "===",
                "max_accounts_per_channel": 5
            }
        }
        result = _load_notification_config(config_data)
        assert result["ENABLE_NOTIFICATION"] is False
        assert result["MESSAGE_BATCH_SIZE"] == 2000
        assert result["DINGTALK_BATCH_SIZE"] == 10000
        assert result["FEISHU_BATCH_SIZE"] == 15000
        assert result["BARK_BATCH_SIZE"] == 1800
        assert result["SLACK_BATCH_SIZE"] == 2000
        assert result["BATCH_SEND_INTERVAL"] == 2.0
        assert result["FEISHU_MESSAGE_SEPARATOR"] == "==="
        assert result["MAX_ACCOUNTS_PER_CHANNEL"] == 5

    def test_load_notification_config_defaults(self) -> None:
        """测试默认值"""
        config_data = {}
        result = _load_notification_config(config_data)
        assert result["ENABLE_NOTIFICATION"] is True
        assert result["MESSAGE_BATCH_SIZE"] == 4000
        assert result["DINGTALK_BATCH_SIZE"] == 20000
        assert result["FEISHU_BATCH_SIZE"] == 29000
        assert result["BARK_BATCH_SIZE"] == 3600
        assert result["SLACK_BATCH_SIZE"] == 4000
        assert result["BATCH_SEND_INTERVAL"] == 1.0
        assert result["FEISHU_MESSAGE_SEPARATOR"] == "---"
        assert result["MAX_ACCOUNTS_PER_CHANNEL"] == 3


class TestLoadPushWindowConfig:
    """测试推送窗口配置加载"""

    def test_load_push_window_config_basic(self) -> None:
        """测试基本推送窗口配置"""
        config_data = {
            "notification": {
                "push_window": {
                    "enabled": True,
                    "start": "09:00",
                    "end": "21:00",
                    "once_per_day": False
                }
            }
        }
        result = _load_push_window_config(config_data)
        assert result["ENABLED"] is True
        assert result["TIME_RANGE"]["START"] == "09:00"
        assert result["TIME_RANGE"]["END"] == "21:00"
        assert result["ONCE_PER_DAY"] is False

    def test_load_push_window_config_defaults(self) -> None:
        """测试默认值"""
        config_data = {}
        result = _load_push_window_config(config_data)
        assert result["ENABLED"] is False
        assert result["TIME_RANGE"]["START"] == "08:00"
        assert result["TIME_RANGE"]["END"] == "22:00"
        assert result["ONCE_PER_DAY"] is True


class TestLoadWeightConfig:
    """测试权重配置加载"""

    def test_load_weight_config_basic(self) -> None:
        """测试基本权重配置"""
        config_data = {
            "advanced": {
                "weight": {
                    "rank": 0.7,
                    "frequency": 0.2,
                    "hotness": 0.1
                }
            }
        }
        result = _load_weight_config(config_data)
        assert result["RANK_WEIGHT"] == 0.7
        assert result["FREQUENCY_WEIGHT"] == 0.2
        assert result["HOTNESS_WEIGHT"] == 0.1

    def test_load_weight_config_defaults(self) -> None:
        """测试默认值"""
        config_data = {}
        result = _load_weight_config(config_data)
        assert result["RANK_WEIGHT"] == 0.6
        assert result["FREQUENCY_WEIGHT"] == 0.3
        assert result["HOTNESS_WEIGHT"] == 0.1


class TestLoadRSSConfig:
    """测试RSS配置加载"""

    def test_load_rss_config_basic(self) -> None:
        """测试基本RSS配置"""
        config_data = {
            "rss": {
                "enabled": True,
                "feeds": ["http://example.com/feed"],
                "freshness_filter": {
                    "enabled": True,
                    "max_age_days": 7
                }
            },
            "advanced": {
                "rss": {
                    "request_interval": 3000,
                    "timeout": 20,
                    "use_proxy": True,
                    "proxy_url": "http://rss-proxy",
                    "notification_enabled": True
                }
            }
        }
        result = _load_rss_config(config_data)
        assert result["ENABLED"] is True
        assert result["REQUEST_INTERVAL"] == 3000
        assert result["TIMEOUT"] == 20
        assert result["USE_PROXY"] is True
        assert result["PROXY_URL"] == "http://rss-proxy"
        assert result["FEEDS"] == ["http://example.com/feed"]
        assert result["FRESHNESS_FILTER"]["ENABLED"] is True
        assert result["FRESHNESS_FILTER"]["MAX_AGE_DAYS"] == 7
        assert result["NOTIFICATION"]["ENABLED"] is True

    def test_load_rss_config_defaults(self) -> None:
        """测试默认值"""
        config_data = {}
        result = _load_rss_config(config_data)
        assert result["ENABLED"] is False
        assert result["REQUEST_INTERVAL"] == 2000
        assert result["TIMEOUT"] == 15
        assert result["USE_PROXY"] is False
        assert result["PROXY_URL"] == ""
        assert result["FEEDS"] == []
        assert result["FRESHNESS_FILTER"]["ENABLED"] is True
        assert result["FRESHNESS_FILTER"]["MAX_AGE_DAYS"] == 3
        assert result["NOTIFICATION"]["ENABLED"] is False

    def test_load_rss_config_negative_max_age(self, capsys: pytest.fixture) -> None:
        """测试负数max_age_days处理"""
        config_data = {
            "rss": {"freshness_filter": {"max_age_days": -5}}
        }
        result = _load_rss_config(config_data)
        assert result["FRESHNESS_FILTER"]["MAX_AGE_DAYS"] == 3
        captured = capsys.readouterr()
        assert "警告" in captured.out
        assert "负数" in captured.out

    def test_load_rss_config_invalid_max_age(self, capsys: pytest.fixture) -> None:
        """测试无效max_age_days处理"""
        config_data = {
            "rss": {"freshness_filter": {"max_age_days": "invalid"}}
        }
        result = _load_rss_config(config_data)
        assert result["FRESHNESS_FILTER"]["MAX_AGE_DAYS"] == 3
        captured = capsys.readouterr()
        assert "警告" in captured.out
        assert "格式错误" in captured.out

    def test_load_rss_config_proxy_fallback(self) -> None:
        """测试代理回退到crawler代理"""
        config_data = {
            "rss": {},
            "advanced": {
                "rss": {},
                "crawler": {"default_proxy": "http://crawler-proxy"}
            }
        }
        result = _load_rss_config(config_data)
        assert result["PROXY_URL"] == "http://crawler-proxy"


class TestLoadStorageConfig:
    """测试存储配置加载"""

    def test_load_storage_config_basic(self) -> None:
        """测试基本存储配置"""
        config_data = {
            "storage": {
                "backend": "local",
                "formats": {"sqlite": False, "txt": False, "html": False},
                "local": {
                    "data_dir": "custom_output",
                    "retention_days": 30
                },
                "remote": {
                    "endpoint_url": "http://s3.example.com",
                    "bucket_name": "test-bucket",
                    "access_key_id": "key_id",
                    "secret_access_key": "secret",
                    "region": "us-east-1",
                    "retention_days": 90
                },
                "pull": {
                    "enabled": True,
                    "days": 14
                }
            }
        }
        result = _load_storage_config(config_data)
        assert result["BACKEND"] == "local"
        assert result["FORMATS"]["SQLITE"] is False
        assert result["FORMATS"]["TXT"] is False
        assert result["FORMATS"]["HTML"] is False
        assert result["LOCAL"]["DATA_DIR"] == "custom_output"
        assert result["LOCAL"]["RETENTION_DAYS"] == 30
        assert result["REMOTE"]["ENDPOINT_URL"] == "http://s3.example.com"
        assert result["REMOTE"]["BUCKET_NAME"] == "test-bucket"
        assert result["REMOTE"]["ACCESS_KEY_ID"] == "key_id"
        assert result["REMOTE"]["SECRET_ACCESS_KEY"] == "secret"
        assert result["REMOTE"]["REGION"] == "us-east-1"
        assert result["REMOTE"]["RETENTION_DAYS"] == 90
        assert result["PULL"]["ENABLED"] is True
        assert result["PULL"]["DAYS"] == 14

    def test_load_storage_config_defaults(self) -> None:
        """测试默认值"""
        config_data = {}
        result = _load_storage_config(config_data)
        assert result["BACKEND"] == "auto"
        assert result["FORMATS"]["SQLITE"] is True
        assert result["FORMATS"]["TXT"] is True
        assert result["FORMATS"]["HTML"] is True
        assert result["LOCAL"]["DATA_DIR"] == "output"
        assert result["LOCAL"]["RETENTION_DAYS"] == 0
        assert result["REMOTE"]["ENDPOINT_URL"] == ""
        assert result["REMOTE"]["BUCKET_NAME"] == ""
        assert result["REMOTE"]["ACCESS_KEY_ID"] == ""
        assert result["REMOTE"]["SECRET_ACCESS_KEY"] == ""
        assert result["REMOTE"]["REGION"] == ""
        assert result["REMOTE"]["RETENTION_DAYS"] == 0
        assert result["PULL"]["ENABLED"] is False
        assert result["PULL"]["DAYS"] == 7


class TestLoadWebhookConfig:
    """测试Webhook配置加载"""

    def test_load_webhook_config_all_channels(self) -> None:
        """测试所有渠道配置"""
        config_data = {
            "notification": {
                "channels": {
                    "feishu": {"webhook_url": "http://feishu.webhook"},
                    "dingtalk": {"webhook_url": "http://dingtalk.webhook"},
                    "wework": {"webhook_url": "http://wework.webhook", "msg_type": "text"},
                    "telegram": {"bot_token": "token123", "chat_id": "chat123"},
                    "email": {"from": "a@example.com", "password": "pass", "to": "b@example.com", "smtp_server": "smtp.example.com", "smtp_port": "587"},
                    "ntfy": {"server_url": "http://ntfy.sh", "topic": "mytopic", "token": "ntfy_token"},
                    "bark": {"url": "http://bark.url"},
                    "slack": {"webhook_url": "http://slack.webhook"}
                }
            }
        }
        result = _load_webhook_config(config_data)
        assert result["FEISHU_WEBHOOK_URL"] == "http://feishu.webhook"
        assert result["DINGTALK_WEBHOOK_URL"] == "http://dingtalk.webhook"
        assert result["WEWORK_WEBHOOK_URL"] == "http://wework.webhook"
        assert result["WEWORK_MSG_TYPE"] == "text"
        assert result["TELEGRAM_BOT_TOKEN"] == "token123"
        assert result["TELEGRAM_CHAT_ID"] == "chat123"
        assert result["EMAIL_FROM"] == "a@example.com"
        assert result["EMAIL_PASSWORD"] == "pass"
        assert result["EMAIL_TO"] == "b@example.com"
        assert result["EMAIL_SMTP_SERVER"] == "smtp.example.com"
        assert result["EMAIL_SMTP_PORT"] == "587"
        assert result["NTFY_SERVER_URL"] == "http://ntfy.sh"
        assert result["NTFY_TOPIC"] == "mytopic"
        assert result["NTFY_TOKEN"] == "ntfy_token"
        assert result["BARK_URL"] == "http://bark.url"
        assert result["SLACK_WEBHOOK_URL"] == "http://slack.webhook"

    def test_load_webhook_config_defaults(self) -> None:
        """测试默认值"""
        config_data = {}
        result = _load_webhook_config(config_data)
        assert result["FEISHU_WEBHOOK_URL"] == ""
        assert result["DINGTALK_WEBHOOK_URL"] == ""
        assert result["WEWORK_WEBHOOK_URL"] == ""
        assert result["WEWORK_MSG_TYPE"] == "markdown"
        assert result["TELEGRAM_BOT_TOKEN"] == ""
        assert result["TELEGRAM_CHAT_ID"] == ""
        assert result["EMAIL_FROM"] == ""
        assert result["EMAIL_PASSWORD"] == ""
        assert result["EMAIL_TO"] == ""
        assert result["EMAIL_SMTP_SERVER"] == ""
        assert result["EMAIL_SMTP_PORT"] == ""
        assert result["NTFY_SERVER_URL"] == "https://ntfy.sh"
        assert result["NTFY_TOPIC"] == ""
        assert result["NTFY_TOKEN"] == ""
        assert result["BARK_URL"] == ""
        assert result["SLACK_WEBHOOK_URL"] == ""


class TestPrintNotificationSources:
    """测试通知渠道打印"""

    def _get_full_config(self, **kwargs: Any) -> Dict[str, Any]:
        """创建包含所有必需键的完整配置"""
        default_config: Dict[str, Any] = {
            "FEISHU_WEBHOOK_URL": "",
            "DINGTALK_WEBHOOK_URL": "",
            "WEWORK_WEBHOOK_URL": "",
            "WEWORK_MSG_TYPE": "markdown",
            "TELEGRAM_BOT_TOKEN": "",
            "TELEGRAM_CHAT_ID": "",
            "EMAIL_FROM": "",
            "EMAIL_PASSWORD": "",
            "EMAIL_TO": "",
            "EMAIL_SMTP_SERVER": "",
            "EMAIL_SMTP_PORT": "",
            "NTFY_SERVER_URL": "",
            "NTFY_TOPIC": "",
            "NTFY_TOKEN": "",
            "BARK_URL": "",
            "SLACK_WEBHOOK_URL": "",
            "MAX_ACCOUNTS_PER_CHANNEL": 3
        }
        default_config.update(kwargs)
        return default_config

    def test_print_feishu_source(self, capsys: pytest.fixture) -> None:
        """测试打印飞书配置来源"""
        config = self._get_full_config(FEISHU_WEBHOOK_URL="http://feishu.webhook")
        _print_notification_sources(config)
        captured = capsys.readouterr()
        assert "飞书" in captured.out
        assert "配置文件" in captured.out

    def test_print_feishu_env_source(self, capsys: pytest.fixture) -> None:
        """测试打印飞书环境变量来源"""
        os.environ["FEISHU_WEBHOOK_URL"] = "http://feishu.env.webhook"
        config = self._get_full_config(FEISHU_WEBHOOK_URL="http://feishu.env.webhook")
        _print_notification_sources(config)
        captured = capsys.readouterr()
        assert "飞书" in captured.out
        assert "环境变量" in captured.out
        del os.environ["FEISHU_WEBHOOK_URL"]

    def test_print_dingtalk_source(self, capsys: pytest.fixture) -> None:
        """测试打印钉钉配置来源"""
        config = self._get_full_config(DINGTALK_WEBHOOK_URL="http://dingtalk.webhook")
        _print_notification_sources(config)
        captured = capsys.readouterr()
        assert "钉钉" in captured.out

    def test_print_wework_source(self, capsys: pytest.fixture) -> None:
        """测试打印企业微信配置来源"""
        config = self._get_full_config(WEWORK_WEBHOOK_URL="http://wework.webhook")
        _print_notification_sources(config)
        captured = capsys.readouterr()
        assert "企业微信" in captured.out

    def test_print_telegram_source(self, capsys: pytest.fixture) -> None:
        """测试打印Telegram配置来源"""
        config = self._get_full_config(
            TELEGRAM_BOT_TOKEN="token123",
            TELEGRAM_CHAT_ID="chat123"
        )
        _print_notification_sources(config)
        captured = capsys.readouterr()
        assert "Telegram" in captured.out

    def test_print_email_source(self, capsys: pytest.fixture) -> None:
        """测试打印邮件配置来源"""
        config = self._get_full_config(
            EMAIL_FROM="a@example.com",
            EMAIL_PASSWORD="pass",
            EMAIL_TO="b@example.com"
        )
        _print_notification_sources(config)
        captured = capsys.readouterr()
        assert "邮件" in captured.out

    def test_print_ntfy_source(self, capsys: pytest.fixture) -> None:
        """测试打印ntfy配置来源"""
        config = self._get_full_config(
            NTFY_SERVER_URL="https://ntfy.sh",
            NTFY_TOPIC="mytopic"
        )
        _print_notification_sources(config)
        captured = capsys.readouterr()
        assert "ntfy" in captured.out

    def test_print_ntfy_with_token(self, capsys: pytest.fixture) -> None:
        """测试打印ntfy配置来源(带token)"""
        config = self._get_full_config(
            NTFY_SERVER_URL="https://ntfy.sh",
            NTFY_TOPIC="topic1;topic2",
            NTFY_TOKEN="token1;token2"
        )
        _print_notification_sources(config)
        captured = capsys.readouterr()
        assert "ntfy" in captured.out
        assert "2个账号" in captured.out

    def test_print_bark_source(self, capsys: pytest.fixture) -> None:
        """测试打印Bark配置来源"""
        config = self._get_full_config(BARK_URL="http://bark.url")
        _print_notification_sources(config)
        captured = capsys.readouterr()
        assert "Bark" in captured.out

    def test_print_slack_source(self, capsys: pytest.fixture) -> None:
        """测试打印Slack配置来源"""
        config = self._get_full_config(SLACK_WEBHOOK_URL="http://slack.webhook")
        _print_notification_sources(config)
        captured = capsys.readouterr()
        assert "Slack" in captured.out

    def test_print_no_channels(self, capsys: pytest.fixture) -> None:
        """测试无配置渠道"""
        config = self._get_full_config()
        _print_notification_sources(config)
        captured = capsys.readouterr()
        assert "未配置任何通知渠道" in captured.out

    def test_print_multi_account_feishu(self, capsys: pytest.fixture) -> None:
        """测试多账号飞书配置"""
        config = self._get_full_config(
            FEISHU_WEBHOOK_URL="http://webhook1;http://webhook2;http://webhook3",
            MAX_ACCOUNTS_PER_CHANNEL=5
        )
        _print_notification_sources(config)
        captured = capsys.readouterr()
        assert "飞书" in captured.out
        assert "3个账号" in captured.out

    def test_print_multi_account_limited(self, capsys: pytest.fixture) -> None:
        """测试多账号限制"""
        config = self._get_full_config(
            FEISHU_WEBHOOK_URL="http://webhook1;http://webhook2;http://webhook3;http://webhook4;http://webhook5",
            MAX_ACCOUNTS_PER_CHANNEL=3
        )
        _print_notification_sources(config)
        captured = capsys.readouterr()
        assert "飞书" in captured.out
        assert "3个账号" in captured.out


class TestLoadConfig:
    """测试完整配置加载"""

    def test_load_config_with_file(self, tmp_path: Path) -> None:
        """测试从文件加载配置"""
        config_content = {
            "app": {"timezone": "UTC"},
            "advanced": {
                "crawler": {"enabled": True},
                "weight": {"rank": 0.7, "frequency": 0.2, "hotness": 0.1}
            },
            "platforms": [{"id": "weibo", "name": "微博"}],
            "rss": {"enabled": False},
            "storage": {"backend": "local"},
            "notification": {"channels": {}},
            "report": {"mode": "daily"}
        }
        config_file = tmp_path / "config.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_content, f)

        result = load_config(str(config_file))
        assert result["TIMEZONE"] == "UTC"
        assert result["ENABLE_CRAWLER"] is True
        assert result["WEIGHT_CONFIG"]["RANK_WEIGHT"] == 0.7
        assert result["PLATFORMS"] == [{"id": "weibo", "name": "微博"}]
        assert result["RSS"]["ENABLED"] is False
        assert result["STORAGE"]["BACKEND"] == "local"

    def test_load_config_with_env_path(self, tmp_path: Path, monkeypatch: pytest.fixture) -> None:
        """测试从环境变量路径加载配置"""
        config_content = {
            "app": {"timezone": "America/New_York"}
        }
        config_file = tmp_path / "config.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_content, f)

        monkeypatch.setenv("CONFIG_PATH", str(config_file))
        result = load_config()
        assert result["TIMEZONE"] == "America/New_York"

    def test_load_config_file_not_found(self) -> None:
        """测试配置文件不存在"""
        with pytest.raises(FileNotFoundError, match="配置文件 .* 不存在"):
            load_config("nonexistent/config.yaml")

    def test_load_config_prints_message(self, tmp_path: Path, capsys: pytest.fixture) -> None:
        """测试配置加载成功消息"""
        config_content = {"app": {}}
        config_file = tmp_path / "config.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_content, f)

        load_config(str(config_file))
        captured = capsys.readouterr()
        assert "配置文件加载成功" in captured.out

    def test_load_config_weight_keys(self, tmp_path: Path) -> None:
        """测试权重配置两个key都存在"""
        config_content = {
            "app": {},
            "advanced": {"weight": {"rank": 0.5, "frequency": 0.3, "hotness": 0.2}}
        }
        config_file = tmp_path / "config.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_content, f)

        result = load_config(str(config_file))
        assert "WEIGHT_CONFIG" in result
        assert "WEIGHT" in result
        assert result["WEIGHT_CONFIG"]["RANK_WEIGHT"] == 0.5
        assert result["WEIGHT"]["RANK_WEIGHT"] == 0.5

    def test_load_config_prints_notification_sources(self, tmp_path: Path, capsys: pytest.fixture) -> None:
        """测试配置加载时打印通知来源"""
        config_content = {
            "app": {},
            "notification": {
                "channels": {
                    "feishu": {"webhook_url": "http://feishu.webhook"}
                }
            }
        }
        config_file = tmp_path / "config.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_content, f)

        load_config(str(config_file))
        captured = capsys.readouterr()
        assert "通知渠道配置来源" in captured.out
        assert "飞书" in captured.out
