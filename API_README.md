# TrendRadar API 集成指南

## 快速开始

TrendRadar 提供了简化的 Python API，方便集成到你的现有项目中。

### 安装

```bash
pip install -r requirements.txt
```

### 基本使用

```python
from trendradar_api import TrendRadarAPI

# 初始化API
api = TrendRadarAPI()

# 抓取新闻
news = api.fetch_news()

# 分析新闻
result = api.analyze_news()

# 获取热点话题
hot_topics = api.get_hot_topics(top_n=10)
```

## API 参考

### TrendRadarAPI

#### 初始化

```python
api = TrendRadarAPI(
    config_path="config/config.yaml",    # 可选：配置文件路径
    keywords_path="config/frequency_words.txt",  # 可选：关键词文件路径
    work_dir="."                         # 可选：工作目录
)
```

#### 主要方法

##### fetch_news()

抓取热点新闻

```python
news = api.fetch_news(
    platforms=["zhihu", "weibo"],  # 可选：指定平台
    max_items=50                   # 可选：每个平台最大抓取数量
)
```

返回格式：
```python
[
    {
        "title": "新闻标题",
        "platform": "平台名称",
        "platform_id": "平台ID",
        "url": "链接",
        "rank": 1,
        "time": "12:00:00",
        "date": "2025-01-02"
    },
    ...
]
```

##### analyze_news()

分析新闻数据

```python
result = api.analyze_news(
    news_data=None,         # 可选：新闻数据（为空则读取最新）
    keywords=["AI", "科技"]  # 可选：关键词列表
)
```

返回格式：
```python
{
    "stats": [
        {
            "keywords": ["AI"],
            "count": 10,
            "titles": [...]
        },
        ...
    ],
    "total": 25,
    "date": "2025-01-02"
}
```

##### filter_by_keywords()

按关键词过滤新闻

```python
filtered = api.filter_by_keywords(
    news_data=news,
    keywords=["科技", "技术"],
    match_type="any"  # "any"=任意匹配, "all"=全部匹配
)
```

##### get_hot_topics()

获取热点话题

```python
hot_topics = api.get_hot_topics(
    top_n=10,       # 返回前N个话题
    min_count=2     # 最小出现次数
)
```

##### get_news_by_date()

获取指定日期的新闻

```python
news = api.get_news_by_date("2025-01-02")
```

##### export_html()

导出HTML报告

```python
html_path = api.export_html(
    news_data=None,            # 可选：新闻数据
    output_path="report.html"  # 可选：输出路径
)
```

## 集成示例

### 示例1: 定时抓取并发送通知

```python
import schedule
from trendradar_api import TrendRadarAPI

def job():
    api = TrendRadarAPI()
    news = api.fetch_news()
    hot_topics = api.get_hot_topics(top_n=5)

    # 发送通知到你的系统
    for topic in hot_topics:
        keywords = " ".join(topic["keywords"])
        send_notification(f"热点: {keywords}, 出现 {topic['count']} 次")

# 每小时执行一次
schedule.every().hour.do(job)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### 示例2: 集成到 Web 应用

```python
from flask import Flask, jsonify
from trendradar_api import TrendRadarAPI

app = Flask(__name__)
api = TrendRadarAPI()

@app.route("/api/news")
def get_news():
    news = api.fetch_news()
    return jsonify(news)

@app.route("/api/hot")
def get_hot():
    hot = api.get_hot_topics(top_n=10)
    return jsonify(hot)

@app.route("/api/analyze")
def analyze():
    result = api.analyze_news()
    return jsonify(result)
```

### 示例3: 数据分析管道

```python
from trendradar_api import TrendRadarAPI
import pandas as pd

api = TrendRadarAPI()

# 抓取新闻
news = api.fetch_news()

# 转换为 DataFrame
df = pd.DataFrame(news)

# 数据分析
platform_stats = df.groupby("platform").size()
print(platform_stats)

# 关键词分析
result = api.analyze_news()
stats_df = pd.DataFrame(result["stats"])
print(stats_df)
```

### 示例4: 异步集成

```python
import asyncio
from trendradar_api import TrendRadarAPI

async def fetch_and_process():
    # 在线程池中执行抓取
    loop = asyncio.get_event_loop()
    api = TrendRadarAPI()

    news = await loop.run_in_executor(None, api.fetch_news)
    hot_topics = await loop.run_in_executor(None, api.get_hot_topics, 10)

    return news, hot_topics

# 使用
news, topics = asyncio.run(fetch_and_process())
```

## 配置说明

### 最小配置

无需配置文件，使用默认设置：

```python
api = TrendRadarAPI()
```

### 完整配置

创建 `config.yaml`:

```yaml
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
  RETENTION_DAYS: 30

WEIGHT:
  RANK: 0.6
  FREQUENCY: 0.3
  HOTNESS: 0.1
```

### 关键词配置

创建 `frequency_words.txt`:

```
# 普通关键词
AI
科技
人工智能

# 必须词（+开头）
+技术

# 过滤词（!开头）
!广告
!推广
```

## 注意事项

1. **请求频率**: 建议每次抓取间隔至少 1 秒
2. **数据存储**: 默认使用 SQLite，数据保存在 `output` 目录
3. **时区设置**: 默认使用北京时间 `Asia/Shanghai`
4. **错误处理**: 所有方法都有异常处理，失败时返回空值

## 性能优化

1. **批量处理**: 一次性抓取所有平台，然后分批处理
2. **缓存数据**: 使用 `get_news_by_date()` 读取历史数据，避免重复抓取
3. **异步处理**: 使用线程池或异步IO处理耗时操作

## 常见问题

### Q: 如何自定义平台列表？

A: 在配置文件中修改 `PLATFORMS` 字段：

```yaml
PLATFORMS:
  - id: zhihu
    name: 知乎
  - id: your-platform-id
    name: 你的平台
```

### Q: 如何添加代理？

A: 在配置文件中设置：

```yaml
USE_PROXY: true
DEFAULT_PROXY: http://proxy.example.com:8080
```

### Q: 如何只抓取不分析？

A: 直接调用 `fetch_news()` 即可，不需要调用 `analyze_news()`。

### Q: 数据存储在哪里？

A: 默认存储在 `output` 目录的 SQLite 数据库中。

## 完整示例

查看 `examples/simple_usage.py` 获取更多使用示例。
