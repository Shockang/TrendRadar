# coding=utf-8
"""
TrendRadar 核心API

提供简化的接口，方便集成到现有工程中
"""

from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any, Union
from datetime import datetime


class TrendRadarAPI:
    """
    TrendRadar 核心API类

    提供简化的热点新闻聚合与分析功能
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        keywords_path: Optional[str] = None,
        work_dir: Optional[str] = None
    ):
        """
        初始化 TrendRadar API

        Args:
            config_path: 配置文件路径（默认：work_dir/config.yaml）
            keywords_path: 关键词文件路径（默认：work_dir/frequency_words.txt）
            work_dir: 工作目录（默认：当前目录）
        """
        from .loader import load_config

        # 设置工作目录
        self.work_dir = Path(work_dir) if work_dir else Path.cwd()

        # 加载配置
        if config_path:
            config = load_config(Path(config_path))
        else:
            config_path = self.work_dir / "config.yaml"
            if config_path.exists():
                config = load_config(config_path)
            else:
                # 使用默认配置
                config = self._get_default_config()

        self.config = config

        # 加载关键词
        self.keywords = []
        self.filter_words = []
        self.global_filters = []

        if keywords_path:
            self._load_keywords(Path(keywords_path))
        else:
            keywords_path = self.work_dir / "frequency_words.txt"
            if keywords_path.exists():
                self._load_keywords(keywords_path)

        # 初始化核心组件
        self._init_components()

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "PLATFORMS": [
                {"id": "zhihu", "name": "知乎"},
                {"id": "weibo", "name": "微博"},
                {"id": "baidu", "name": "百度热搜"},
            ],
            "REQUEST_INTERVAL": 1000,
            "TIMEZONE": "Asia/Shanghai",
            "REPORT_MODE": "daily",
            "RANK_THRESHOLD": 5,
            "USE_PROXY": False,
            "DEFAULT_PROXY": "",
            "ENABLE_CRAWLER": True,
            "ENABLE_NOTIFICATION": False,
            "STORAGE": {
                "BACKEND": "local",
                "DATA_DIR": "output",
                "FORMATS": {
                    "SQLITE": True,
                    "TXT": False,
                    "HTML": True,
                },
                "RETENTION_DAYS": 0,
            },
            "WEIGHT": {
                "RANK": 0.6,
                "FREQUENCY": 0.3,
                "HOTNESS": 0.1,
            },
            "VERSION_CHECK_URL": "",
            "SHOW_VERSION_UPDATE": False,
        }

    def _load_keywords(self, keywords_path: Path) -> None:
        """加载关键词配置"""
        try:
            from .frequency import parse_word_groups

            with open(keywords_path, "r", encoding="utf-8") as f:
                content = f.read()

            word_groups, filter_words, global_filters = parse_word_groups(content)
            self.keywords = word_groups
            self.filter_words = filter_words
            self.global_filters = global_filters
        except Exception as e:
            print(f"加载关键词文件失败: {e}")

    def _init_components(self) -> None:
        """初始化核心组件"""
        from ..crawler import DataFetcher
        from ..storage import StorageManager
        from .data import convert_crawl_results_to_news_data

        # 初始化爬虫
        proxy_url = self.config.get("DEFAULT_PROXY", "") if self.config.get("USE_PROXY") else None
        self.fetcher = DataFetcher(proxy_url=proxy_url)

        # 初始化存储
        storage_config = self.config.get("STORAGE", {})
        data_dir = self.work_dir / storage_config.get("DATA_DIR", "output")
        self.storage = StorageManager(
            backend=storage_config.get("BACKEND", "local"),
            data_dir=str(data_dir)
        )

        # 时区
        self.timezone = self.config.get("TIMEZONE", "Asia/Shanghai")

    def fetch_news(
        self,
        platforms: Optional[List[str]] = None,
        max_items: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        抓取热点新闻

        Args:
            platforms: 平台ID列表（为空则使用配置中的平台）
            max_items: 每个平台最大抓取数量

        Returns:
            新闻数据列表
        """
        # 确定平台列表
        if platforms:
            platform_list = [(p, p) for p in platforms]
        else:
            platforms_config = self.config.get("PLATFORMS", [])
            platform_list = [(p["id"], p.get("name", p["id"])) for p in platforms_config]

        # 抓取数据
        results, id_to_name, failed_ids = self.fetcher.crawl_websites(
            platform_list,
            self.config.get("REQUEST_INTERVAL", 1000)
        )

        # 转换为统一格式
        crawl_time = datetime.now().strftime("%H:%M:%S")
        crawl_date = datetime.now().strftime("%Y-%m-%d")

        from .data import convert_crawl_results_to_news_data
        news_data = convert_crawl_results_to_news_data(
            results, id_to_name, failed_ids, crawl_time, crawl_date
        )

        # 保存到存储
        self.storage.save_news_data(news_data)

        return news_data.to_dict()

    def analyze_news(
        self,
        news_data: Optional[List[Dict[str, Any]]] = None,
        keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        分析新闻数据

        Args:
            news_data: 新闻数据（为空则从存储读取最新数据）
            keywords: 关键词列表（为空则使用配置中的关键词）

        Returns:
            分析结果统计
        """
        from .analyzer import count_frequency
        from ..storage import convert_news_data_to_results

        # 获取数据
        if not news_data:
            # 从存储读取最新数据
            date_str = datetime.now().strftime("%Y-%m-%d")
            news_data = self.storage.get_news_data_by_date(date_str)
            if not news_data:
                return {"error": "没有可用的新闻数据"}

        # 转换格式
        results, id_to_name = convert_news_data_to_results(news_data)

        # 构建标题信息
        title_info = {}
        for source_id, titles_data in results.items():
            title_info[source_id] = {}
            for title, data in titles_data.items():
                title_info[source_id][title] = {
                    "first_time": data.get("time", ""),
                    "last_time": data.get("time", ""),
                    "count": 1,
                    "ranks": data.get("ranks", []),
                    "url": data.get("url", ""),
                    "mobileUrl": data.get("mobileUrl", ""),
                }

        # 获取关键词
        word_groups = []
        if keywords:
            word_groups = [{"words": keywords, "must_words": [], "limit": 0}]
        elif self.keywords:
            word_groups = self.keywords

        # 统计频率
        stats, total = count_frequency(
            results,
            word_groups,
            self.filter_words,
            id_to_name,
            title_info,
            {},
            mode="daily",
            global_filters=self.global_filters,
            quiet=True
        )

        return {
            "stats": stats,
            "total": total,
            "date": datetime.now().strftime("%Y-%m-%d"),
        }

    def filter_by_keywords(
        self,
        news_data: List[Dict[str, Any]],
        keywords: List[str],
        match_type: str = "any"
    ) -> List[Dict[str, Any]]:
        """
        按关键词过滤新闻

        Args:
            news_data: 新闻数据列表
            keywords: 关键词列表
            match_type: 匹配类型（any=任意匹配，all=全部匹配）

        Returns:
            过滤后的新闻列表
        """
        from .frequency import matches_word_groups

        word_groups = [{"words": keywords, "must_words": [] if match_type == "any" else keywords, "limit": 0}]

        filtered = []
        for news in news_data:
            title = news.get("title", "")
            if matches_word_groups(title, word_groups, [], []):
                filtered.append(news)

        return filtered

    def get_hot_topics(
        self,
        top_n: int = 10,
        min_count: int = 2
    ) -> List[Dict[str, Any]]:
        """
        获取热点话题

        Args:
            top_n: 返回前N个话题
            min_count: 最小出现次数

        Returns:
            热点话题列表
        """
        analysis = self.analyze_news()

        if "stats" not in analysis:
            return []

        # 按数量排序
        sorted_stats = sorted(
            analysis["stats"],
            key=lambda x: x["count"],
            reverse=True
        )

        # 过滤并限制数量
        filtered = [
            stat for stat in sorted_stats
            if stat["count"] >= min_count
        ][:top_n]

        return filtered

    def get_news_by_date(
        self,
        date: str
    ) -> Optional[List[Dict[str, Any]]]:
        """
        获取指定日期的新闻

        Args:
            date: 日期字符串（YYYY-MM-DD）

        Returns:
            新闻数据列表
        """
        return self.storage.get_news_data_by_date(date)

    def export_html(
        self,
        news_data: Optional[List[Dict[str, Any]]] = None,
        output_path: Optional[Union[str, Path]] = None
    ) -> Optional[str]:
        """
        导出HTML报告

        Args:
            news_data: 新闻数据（为空则使用最新数据）
            output_path: 输出路径（为空则自动生成）

        Returns:
            HTML文件路径
        """
        from ..report.generator import generate_html_report

        if not news_data:
            analysis = self.analyze_news()
            if "stats" in analysis:
                stats = analysis["stats"]
                total = analysis["total"]
            else:
                return None
        else:
            analysis = self.analyze_news(news_data)
            stats = analysis["stats"]
            total = analysis["total"]

        # 生成HTML
        if not output_path:
            output_path = self.work_dir / "output" / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        else:
            output_path = Path(output_path)

        html_content = generate_html_report(
            stats=stats,
            total=total,
            date=datetime.now().strftime("%Y-%m-%d"),
            time=datetime.now().strftime("%H:%M:%S"),
        )

        # 保存文件
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return str(output_path)
