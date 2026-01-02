# coding=utf-8
"""
简单使用示例

展示如何使用 TrendRadar API 进行基本操作
"""

from trendradar_api import TrendRadarAPI


def example_1_fetch_news():
    """示例1: 抓取热点新闻"""
    print("=== 示例1: 抓取热点新闻 ===\n")

    # 初始化API（使用默认配置）
    api = TrendRadarAPI()

    # 抓取新闻
    news = api.fetch_news()

    print(f"抓取到 {len(news)} 条新闻")
    if news:
        print(f"第一条: {news[0]['title']}")


def example_2_analyze_news():
    """示例2: 分析新闻"""
    print("\n=== 示例2: 分析新闻 ===\n")

    # 初始化API
    api = TrendRadarAPI()

    # 先抓取新闻
    api.fetch_news()

    # 分析新闻（使用默认关键词）
    result = api.analyze_news()

    if "stats" in result:
        print(f"分析结果: 共 {result['total']} 条匹配")
        for stat in result["stats"][:5]:
            keywords = " ".join(stat["keywords"])
            print(f"  - {keywords}: {stat['count']} 条")


def example_3_custom_keywords():
    """示例3: 使用自定义关键词"""
    print("\n=== 示例3: 使用自定义关键词 ===\n")

    # 初始化API
    api = TrendRadarAPI()

    # 抓取新闻
    api.fetch_news()

    # 使用自定义关键词分析
    keywords = ["AI", "人工智能", "ChatGPT"]
    result = api.analyze_news(keywords=keywords)

    if "stats" in result:
        print(f"匹配到 {result['total']} 条关于AI的新闻")


def example_4_filter_news():
    """示例4: 过滤新闻"""
    print("\n=== 示例4: 过滤新闻 ===\n")

    # 初始化API
    api = TrendRadarAPI()

    # 抓取新闻
    all_news = api.fetch_news()

    # 按关键词过滤
    keywords = ["科技", "技术"]
    filtered = api.filter_by_keywords(all_news, keywords)

    print(f"从 {len(all_news)} 条新闻中筛选出 {len(filtered)} 条")


def example_5_hot_topics():
    """示例5: 获取热点话题"""
    print("\n=== 示例5: 获取热点话题 ===\n")

    # 初始化API
    api = TrendRadarAPI()

    # 先抓取新闻
    api.fetch_news()

    # 获取热点话题（前10个，至少出现2次）
    hot_topics = api.get_hot_topics(top_n=10, min_count=2)

    print(f"发现 {len(hot_topics)} 个热点话题:")
    for i, topic in enumerate(hot_topics, 1):
        keywords = " ".join(topic["keywords"])
        print(f"  {i}. {keywords}: {topic['count']} 次")


def example_6_export_html():
    """示例6: 导出HTML报告"""
    print("\n=== 示例6: 导出HTML报告 ===\n")

    # 初始化API
    api = TrendRadarAPI()

    # 抓取并分析新闻
    api.fetch_news()

    # 导出HTML
    html_path = api.export_html()

    if html_path:
        print(f"HTML报告已生成: {html_path}")
    else:
        print("生成HTML报告失败")


def example_7_custom_config():
    """示例7: 使用自定义配置"""
    print("\n=== 示例7: 使用自定义配置 ===\n")

    # 初始化API（指定配置文件路径）
    api = TrendRadarAPI(
        config_path="config/config.yaml",
        keywords_path="config/frequency_words.txt",
        work_dir="."
    )

    # 抓取新闻
    news = api.fetch_news()

    print(f"使用自定义配置抓取到 {len(news)} 条新闻")


def example_8_integration():
    """示例8: 集成到现有项目"""
    print("\n=== 示例8: 集成到现有项目 ===\n")

    # 在你的项目中使用
    api = TrendRadarAPI()

    # 定时抓取新闻
    news = api.fetch_news()

    # 获取热点话题
    hot_topics = api.get_hot_topics(top_n=5)

    # 处理热点话题（例如：推送到你的系统）
    for topic in hot_topics:
        keywords = " ".join(topic["keywords"])
        count = topic["count"]

        # 这里可以添加你的业务逻辑
        print(f"热点: {keywords}, 出现 {count} 次")

        # 例如：发送到你的消息队列
        # send_to_queue(keywords, count)

        # 例如：存储到你的数据库
        # save_to_database(keywords, count)


if __name__ == "__main__":
    # 运行所有示例
    example_1_fetch_news()
    example_2_analyze_news()
    example_3_custom_keywords()
    example_4_filter_news()
    example_5_hot_topics()
    example_6_export_html()
    example_7_custom_config()
    example_8_integration()
