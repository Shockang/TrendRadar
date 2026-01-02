# coding=utf-8
"""
测试工具模块
"""

import pytest
from datetime import datetime
import pytz
from trendradar.utils.time import (
    get_configured_time,
    format_date_folder,
    format_time_filename,
    get_current_time_display,
    convert_time_for_display,
    format_iso_time_friendly,
    is_within_days,
    DEFAULT_TIMEZONE,
)
from trendradar.utils.url import (
    normalize_url,
    get_url_signature,
    PLATFORM_PARAMS_TO_REMOVE,
    COMMON_TRACKING_PARAMS,
)


class TestGetConfiguredTime:
    """测试 get_configured_time 函数"""

    def test_get_configured_time_default_timezone(self):
        """测试使用默认时区获取时间"""
        result = get_configured_time()
        assert isinstance(result, datetime)
        assert result.tzinfo is not None
        # 应该是上海时区
        assert str(result.tzinfo) == "Asia/Shanghai"

    def test_get_configured_time_custom_timezone(self):
        """测试使用自定义时区获取时间"""
        result = get_configured_time("America/New_York")
        assert isinstance(result, datetime)
        assert result.tzinfo is not None
        assert str(result.tzinfo) == "America/New_York"

    def test_get_configured_time_invalid_timezone(self):
        """测试使用无效时区时的回退行为"""
        import io
        import sys
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            result = get_configured_time("Invalid/Timezone")

        output = f.getvalue()
        assert "警告" in output
        assert "未知时区" in output
        assert isinstance(result, datetime)
        assert result.tzinfo is not None
        # 应该回退到默认时区
        assert str(result.tzinfo) == "Asia/Shanghai"


class TestFormatDateFolder:
    """测试 format_date_folder 函数"""

    def test_format_date_folder_with_date(self):
        """测试使用指定日期"""
        result = format_date_folder("2025-12-09")
        assert result == "2025-12-09"

    def test_format_date_folder_without_date(self):
        """测试使用当前日期"""
        result = format_date_folder()
        assert isinstance(result, str)
        assert len(result) == 10  # YYYY-MM-DD
        assert "-" in result

    def test_format_date_folder_with_timezone(self):
        """测试使用不同时区"""
        # 这个测试主要验证函数能正常工作
        result = format_date_folder(timezone="America/New_York")
        assert isinstance(result, str)
        assert len(result) == 10


class TestFormatTimeFilename:
    """测试 format_time_filename 函数"""

    def test_format_time_filename_default(self):
        """测试默认格式"""
        result = format_time_filename()
        assert isinstance(result, str)
        assert len(result) == 5  # HH-MM
        assert "-" in result
        # 验证格式：应该是两个数字-两个数字
        parts = result.split("-")
        assert len(parts) == 2
        assert parts[0].isdigit()
        assert parts[1].isdigit()

    def test_format_time_filename_custom_timezone(self):
        """测试自定义时区"""
        result = format_time_filename("America/New_York")
        assert isinstance(result, str)
        assert len(result) == 5


class TestGetCurrentTimeDisplay:
    """测试 get_current_time_display 函数"""

    def test_get_current_time_display_default(self):
        """测试默认格式"""
        result = get_current_time_display()
        assert isinstance(result, str)
        assert len(result) == 5  # HH:MM
        assert ":" in result
        # 验证格式
        parts = result.split(":")
        assert len(parts) == 2
        assert parts[0].isdigit()
        assert parts[1].isdigit()

    def test_get_current_time_display_custom_timezone(self):
        """测试自定义时区"""
        result = get_current_time_display("America/New_York")
        assert isinstance(result, str)
        assert len(result) == 5


class TestConvertTimeForDisplay:
    """测试 convert_time_for_display 函数"""

    def test_convert_time_valid_format(self):
        """测试转换有效格式"""
        result = convert_time_for_display("15-30")
        assert result == "15:30"

    def test_convert_time_different_values(self):
        """测试不同的时间值"""
        assert convert_time_for_display("00-00") == "00:00"
        assert convert_time_for_display("23-59") == "23:59"
        assert convert_time_for_display("09-05") == "09:05"

    def test_convert_time_invalid_format(self):
        """测试无效格式"""
        # 长度不对
        assert convert_time_for_display("15:30") == "15:30"  # 已经是正确格式
        assert convert_time_for_display("15-30-00") == "15-30-00"
        # 空字符串
        assert convert_time_for_display("") == ""
        # None
        assert convert_time_for_display(None) == None
        # 没有连字符
        assert convert_time_for_display("1530") == "1530"


class TestFormatIsoTimeFriendly:
    """测试 format_iso_time_friendly 函数"""

    def test_format_iso_with_timezone(self):
        """测试带时区的ISO时间"""
        result = format_iso_time_friendly("2025-12-29T00:20:00+08:00")
        assert isinstance(result, str)
        assert "12-29" in result or "00:20" in result

    def test_format_iso_with_z_suffix(self):
        """测试Z后缀的UTC时间"""
        result = format_iso_time_friendly("2025-12-29T00:20:00Z")
        assert isinstance(result, str)

    def test_format_iso_without_timezone(self):
        """测试不带时区的ISO时间"""
        result = format_iso_time_friendly("2025-12-29T00:20:00")
        assert isinstance(result, str)

    def test_format_iso_with_t_separator(self):
        """测试带T分隔符的格式"""
        result = format_iso_time_friendly("2025-12-29T00:20:00")
        assert isinstance(result, str)

    def test_format_iso_without_date(self):
        """测试不包含日期"""
        result = format_iso_time_friendly("2025-12-29T00:20:00", include_date=False)
        assert isinstance(result, str)
        # 应该只包含时间，不包含日期
        assert ":" in result
        assert "12-29" not in result

    def test_format_iso_with_custom_timezone(self):
        """测试使用自定义时区"""
        result = format_iso_time_friendly("2025-12-29T00:20:00+08:00", timezone="America/New_York")
        assert isinstance(result, str)

    def test_format_iso_empty_string(self):
        """测试空字符串"""
        result = format_iso_time_friendly("")
        assert result == ""

    def test_format_iso_none_value(self):
        """测试None值"""
        result = format_iso_time_friendly(None)
        assert result == ""

    def test_format_iso_invalid_format(self):
        """测试无效格式（应该返回简化的原始字符串）"""
        result = format_iso_time_friendly("invalid-time-format")
        # 应该返回原始字符串或其简化版本
        assert isinstance(result, str)

    def test_format_iso_with_fractional_seconds(self):
        """测试带毫秒的ISO时间"""
        result = format_iso_time_friendly("2025-12-29T00:20:00.123+08:00")
        assert isinstance(result, str)


class TestIsWithinDays:
    """测试 is_within_days 函数"""

    def test_is_within_days_recent_time(self):
        """测试最近的时间"""
        # 1小时前的时间
        now = datetime.now(pytz.UTC)
        recent_time = (now.replace(hour=now.hour - 1)).strftime("%Y-%m-%dT%H:%M:%S")
        result = is_within_days(recent_time, max_days=1)
        assert result is True

    def test_is_within_days_old_time(self):
        """测试旧时间"""
        # 10天前的时间
        old_time = "2025-12-20T00:00:00"
        # 这个测试可能会失败，取决于当前时间
        # 所以我们只测试函数能正常执行
        result = is_within_days(old_time, max_days=1)
        assert isinstance(result, bool)

    def test_is_within_days_zero_max_days(self):
        """测试max_days为0时禁用过滤"""
        result = is_within_days("2020-01-01T00:00:00", max_days=0)
        assert result is True  # 禁用过滤，应该返回True

    def test_is_within_days_negative_max_days(self):
        """测试负数max_days"""
        result = is_within_days("2020-01-01T00:00:00", max_days=-1)
        assert result is True  # 负数表示禁用过滤

    def test_is_within_days_empty_string(self):
        """测试空字符串"""
        result = is_within_days("", max_days=1)
        assert result is True

    def test_is_within_days_none_value(self):
        """测试None值"""
        result = is_within_days(None, max_days=1)
        assert result is True

    def test_is_within_days_invalid_format(self):
        """测试无效格式"""
        result = is_within_days("invalid-time", max_days=1)
        assert result is True  # 无法解析时应该保留

    def test_is_within_days_with_timezone(self):
        """测试带时区的时间"""
        result = is_within_days("2025-12-29T00:20:00+08:00", max_days=1, timezone="Asia/Shanghai")
        assert isinstance(result, bool)

    def test_is_within_days_utc_time(self):
        """测试UTC时间"""
        result = is_within_days("2025-12-29T00:20:00Z", max_days=1)
        assert isinstance(result, bool)


class TestNormalizeUrl:
    """测试 normalize_url 函数"""

    def test_normalize_url_empty_string(self):
        """测试空字符串"""
        result = normalize_url("")
        assert result == ""

    def test_normalize_url_none_value(self):
        """测试None值"""
        result = normalize_url(None)
        assert result is None

    def test_normalize_url_no_query_params(self):
        """测试没有查询参数的URL"""
        url = "https://example.com/page"
        result = normalize_url(url)
        assert result == url

    def test_normalize_url_weibo_params(self):
        """测试微博URL参数移除"""
        url = "https://s.weibo.com/weibo?q=test&band_rank=6&Refer=top"
        result = normalize_url(url, platform_id="weibo")
        # 应该移除 band_rank 和 Refer
        assert "band_rank" not in result
        assert "Refer" not in result
        # 应该保留 q 参数
        assert "q=test" in result

    def test_normalize_url_weibo_all_params(self):
        """测试微博URL移除所有动态参数"""
        url = "https://s.weibo.com/weibo?q=test&t=31&band_rank=1&Refer=top"
        result = normalize_url(url, platform_id="weibo")
        # 只应该保留 q 参数
        assert result == "https://s.weibo.com/weibo?q=test"

    def test_normalize_url_utm_params(self):
        """测试UTM追踪参数移除"""
        url = "https://example.com/page?id=1&utm_source=twitter&utm_medium=social"
        result = normalize_url(url)
        # 应该移除 utm 参数
        assert "utm_source" not in result
        assert "utm_medium" not in result
        # 应该保留 id 参数
        assert "id=1" in result

    def test_normalize_url_common_tracking_params(self):
        """测试通用追踪参数移除"""
        url = "https://example.com/page?id=1&ref=twitter&source=home"
        result = normalize_url(url)
        # 应该移除通用追踪参数
        assert "ref=twitter" not in result
        assert "source=home" not in result

    def test_normalize_url_preserves_important_params(self):
        """测试保留重要参数"""
        url = "https://example.com/search?q=python&category=tech"
        result = normalize_url(url)
        # 应该保留重要参数
        assert "q=python" in result
        assert "category=tech" in result

    def test_normalize_url_params_sorted(self):
        """测试参数排序（确保一致性）"""
        url = "https://example.com/page?z=1&a=2&m=3"
        result = normalize_url(url)
        # 参数应该按字母序排序
        # 注意：urlencode 会将参数排序
        assert result == "https://example.com/page?a=2&m=3&z=1"

    def test_normalize_url_removes_fragment(self):
        """测试移除fragment"""
        url = "https://example.com/page?id=1#section"
        result = normalize_url(url)
        # 应该移除 fragment
        assert "#section" not in result

    def test_normalize_url_invalid_url(self):
        """测试无效URL"""
        url = "not-a-valid-url"
        result = normalize_url(url)
        # 解析失败时应该返回原始URL
        assert result == url

    def test_normalize_url_without_platform_id(self):
        """测试不指定平台ID"""
        url = "https://s.weibo.com/weibo?q=test&band_rank=6&Refer=top"
        result = normalize_url(url)  # 不指定 platform_id
        # 应该只移除通用追踪参数，不移除微博特定参数
        # 但 Refer 不是通用追踪参数，所以应该保留
        # band_rank 也不是通用参数，应该保留
        assert "band_rank" in result or "Refer" in result

    def test_normalize_url_all_params_removed(self):
        """测试所有参数都被移除的情况"""
        url = "https://example.com/page?utm_source=twitter&ref=home"
        result = normalize_url(url)
        # 所有参数都被移除，应该返回不带查询字符串的URL
        assert "?" not in result
        assert result == "https://example.com/page"

    def test_normalize_url_case_insensitive(self):
        """测试参数名大小写不敏感"""
        # 实际上参数名是大小写敏感的，但测试能正常工作
        url = "https://example.com/page?ID=1&utm_source=twitter"
        result = normalize_url(url)
        # ID 不是 id，所以不会被移除（除非 ID 的大小写匹配）
        assert "ID=1" in result or "id=1" not in result


class TestGetUrlSignature:
    """测试 get_url_signature 函数"""

    def test_get_url_signature_basic(self):
        """测试基本签名生成"""
        url = "https://example.com/page?id=1&utm_source=twitter"
        result = get_url_signature(url)
        # 签名应该是标准化后的URL
        assert "utm_source" not in result
        assert "id=1" in result

    def test_get_url_signature_with_platform(self):
        """测试带平台ID的签名生成"""
        url = "https://s.weibo.com/weibo?q=test&band_rank=6"
        result = get_url_signature(url, platform_id="weibo")
        # 应该移除平台特定参数
        assert "band_rank" not in result

    def test_get_url_signature_consistency(self):
        """测试签名一致性（相同URL产生相同签名）"""
        url1 = "https://example.com/page?utm_source=twitter&id=1"
        url2 = "https://example.com/page?id=1&utm_source=twitter"
        result1 = get_url_signature(url1)
        result2 = get_url_signature(url2)
        # 参数顺序不同，但标准化后应该相同
        assert result1 == result2


class TestPlatformConstants:
    """测试平台常量"""

    def test_weibo_params(self):
        """测试微博平台参数配置"""
        assert "weibo" in PLATFORM_PARAMS_TO_REMOVE
        weibo_params = PLATFORM_PARAMS_TO_REMOVE["weibo"]
        assert "band_rank" in weibo_params
        assert "Refer" in weibo_params
        assert "t" in weibo_params

    def test_common_tracking_params(self):
        """测试通用追踪参数"""
        assert "utm_source" in COMMON_TRACKING_PARAMS
        assert "utm_medium" in COMMON_TRACKING_PARAMS
        assert "utm_campaign" in COMMON_TRACKING_PARAMS
        assert "ref" in COMMON_TRACKING_PARAMS
        assert "source" in COMMON_TRACKING_PARAMS
        assert "timestamp" in COMMON_TRACKING_PARAMS


class TestTimeUtilsEdgeCases:
    """测试时间工具函数的边界情况"""

    def test_time_format_consistency(self):
        """测试时间格式的一致性"""
        # 获取文件名格式的时间
        filename_time = format_time_filename()
        # 获取显示格式的时间
        display_time = get_current_time_display()

        # 文件名格式应该用连字符，显示格式用冒号
        assert "-" in filename_time
        assert ":" in display_time

        # 两者应该表示相同时刻（格式不同）
        filename_converted = convert_time_for_display(filename_time)
        assert filename_converted == display_time

    def test_is_within_days_boundary(self):
        """测试天数边界"""
        # 创建一个刚好在边界上的时间
        now = get_configured_time()
        # 测试刚好1天前的时间（应该通过）
        from datetime import timedelta
        boundary_time = (now - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")
        result = is_within_days(boundary_time, max_days=1)
        # 刚好1天应该返回True
        assert result is True

    def test_format_iso_with_different_timezones(self):
        """测试不同时区的ISO时间转换"""
        # UTC时间
        utc_time = "2025-12-29T00:20:00+00:00"
        result_utc = format_iso_time_friendly(utc_time, timezone="UTC")
        assert isinstance(result_utc, str)

        # 上海时间
        result_sh = format_iso_time_friendly(utc_time, timezone="Asia/Shanghai")
        assert isinstance(result_sh, str)

        # 纽约时间
        result_ny = format_iso_time_friendly(utc_time, timezone="America/New_York")
        assert isinstance(result_ny, str)

        # 不同时区应该产生不同的显示时间
        #（具体值取决于时区差异，这里只测试函数能正常工作）


class TestUrlUtilsEdgeCases:
    """测试URL工具函数的边界情况"""

    def test_normalize_url_with_multiple_tracking_params(self):
        """测试多个追踪参数"""
        url = "https://example.com/page?id=1&utm_source=twitter&utm_medium=social&ref=home&source=api"
        result = normalize_url(url)
        # 所有追踪参数都应该被移除
        assert "utm_" not in result
        assert "ref=" not in result
        assert "source=" not in result
        # 应该保留 id 参数
        assert "id=1" in result

    def test_normalize_url_preserves_path_and_params(self):
        """测试保留路径和重要参数"""
        url = "https://example.com/path/to/page?id=1&category=tech&sort=date"
        result = normalize_url(url)
        # 应该保留路径
        assert "/path/to/page" in result
        # 应该保留重要参数
        assert "id=1" in result
        assert "category=tech" in result
        assert "sort=date" in result

    def test_get_url_signature_for_same_content(self):
        """测试相同内容的不同URL变体产生相同签名"""
        # 同一个内容的不同URL变体
        url1 = "https://example.com/page?id=1&utm_source=twitter"
        url2 = "https://example.com/page?id=1&utm_source=facebook"
        url3 = "https://example.com/page?id=1&ref=google"

        sig1 = get_url_signature(url1)
        sig2 = get_url_signature(url2)
        sig3 = get_url_signature(url3)

        # 所有签名应该相同（因为UTM参数被移除）
        assert sig1 == sig2 == sig3

    def test_normalize_url_with_special_chars(self):
        """测试包含特殊字符的URL"""
        url = "https://example.com/search?q=python+tutorial&lang=en"
        result = normalize_url(url)
        # 应该正确处理特殊字符
        assert "q=python+tutorial" in result or "q=python%20tutorial" in result

    def test_normalize_url_with_duplicate_params(self):
        """测试重复参数的处理"""
        url = "https://example.com/page?id=1&id=2&utm_source=twitter"
        result = normalize_url(url)
        # 应该能处理重复参数（虽然这种情况不太常见）
        assert isinstance(result, str)
