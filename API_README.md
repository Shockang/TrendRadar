# TrendRadar API 集成指南

## 快速开始

TrendRadar 提供了简化的 Python API，方便集成到你的现有项目中。

### 安装

#### 最小化安装（仅核心功能）

```bash
# 只安装核心依赖
pip install -r requirements-core.txt

# 或者使用 setup.py
pip install -e .
```

#### 完整安装（包含所有功能）

```bash
# 安装所有依赖
pip install -r requirements-all.txt

# 或者使用 extras
pip install -e ".[all]"
```

#### 按需安装

```bash
# 核心功能 + MCP 服务
pip install -e ".[mcp]"

# 核心功能 + 云存储
pip install -e ".[storage]"

# 核心功能 + 开发工具
pip install -e ".[dev]"
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

## 依赖说明

### 核心依赖（requirements-core.txt）

这些是运行 TrendRadar 核心功能所需的最低依赖：

- **requests** (>=2.32.5): HTTP 请求库
- **pytz** (>=2025.2): 时区处理
- **PyYAML** (>=6.0.3): YAML 配置文件解析
- **feedparser** (>=6.0.0): RSS 订阅源解析

### 可选依赖

#### 云存储功能（requirements-storage.txt）

- **boto3** (>=1.35.0): AWS S3 存储

如果你需要使用云存储功能（S3等），需要额外安装：

```bash
pip install -r requirements-storage.txt
```

#### MCP 服务（requirements-mcp.txt）

- **fastmcp** (>=2.12.0): MCP 服务器
- **websockets** (>=13.0): WebSocket 支持

如果你需要使用 MCP 服务和 AI 分析功能，需要额外安装：

```bash
pip install -r requirements-mcp.txt
```

#### 开发工具（requirements-dev.txt）

- **pytest** (>=7.0.0): 单元测试
- **pytest-cov** (>=4.0.0): 测试覆盖率
- **black** (>=22.0.0): 代码格式化
- **flake8** (>=4.0.0): 代码检查
- **pylint** (>=2.12.0): 代码质量检查
- **mypy** (>=1.0.0): 类型检查

如果你需要参与开发或运行测试，需要安装开发工具：

```bash
pip install -r requirements-dev.txt
```

## 测试

### 运行测试

```bash
# 运行所有测试
pytest

# 运行测试并显示详细输出
pytest -v

# 运行测试并生成覆盖率报告
pytest --cov=trendradar --cov-report=html

# 运行特定测试文件
pytest tests/test_api.py

# 运行特定测试类
pytest tests/test_api.py::TestTrendRadarAPI

# 运行特定测试方法
pytest tests/test_api.py::TestTrendRadarAPI::test_init_with_defaults
```

### 测试说明

项目包含两类测试：

1. **单元测试**: 不需要网络连接，可以快速运行
   - 测试 API 初始化
   - 测试关键词过滤
   - 测试配置加载

2. **集成测试**: 需要网络连接
   - 测试完整的抓取流程
   - 测试数据存储和分析
   - 使用 `@pytest.mark.integration` 标记

跳过集成测试：

```bash
pytest -m "not integration"
```

只运行集成测试：

```bash
pytest -m integration
```

## 开发指南

### 代码格式化

```bash
# 格式化代码
black trendradar/ tests/ examples/

# 检查代码风格
flake8 trendradar/ tests/ examples/

# 代码质量检查
pylint trendradar/
```

### 类型检查

```bash
# 类型检查
mypy trendradar/
```

### 贡献代码

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

提交前请确保：

- 所有测试通过 (`pytest`)
- 代码通过格式检查 (`black --check`)
- 代码通过风格检查 (`flake8`)
- 添加了必要的测试用例
- 更新了相关文档

## 版本历史

### v5.0.0 (当前版本)

- ✨ 新增简化的 API 接口
- ✨ 支持作为 Python 库集成
- ✨ 添加类型注解
- ✨ 分离核心依赖和可选依赖
- ✨ 添加完整的单元测试
- 📝 完善文档和示例

### 旧版本

详见 [主项目文档](README.md)
