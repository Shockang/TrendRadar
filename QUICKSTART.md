# TrendRadar 快速开始

## 作为 Python 库使用

### 1. 最小化安装

```bash
# 克隆项目
git clone https://github.com/sansan0/TrendRadar.git
cd TrendRadar

# 安装核心依赖
pip install -r requirements-core.txt

# 或者直接安装
pip install -e .
```

### 2. 基本使用

```python
from trendradar_api import TrendRadarAPI

# 初始化
api = TrendRadarAPI()

# 抓取新闻
news = api.fetch_news()

# 获取热点话题
hot_topics = api.get_hot_topics(top_n=10)

# 打印结果
for topic in hot_topics:
    keywords = " ".join(topic["keywords"])
    print(f"{keywords}: {topic['count']} 次")
```

### 3. 运行示例

```bash
# 查看所有示例
python examples/simple_usage.py
```

## 作为命令行工具使用

### 1. 安装

```bash
# 克隆项目
git clone https://github.com/sansan0/TrendRadar.git
cd TrendRadar

# 安装依赖
pip install -r requirements.txt
```

### 2. 运行

```bash
# 使用默认配置运行
python -m trendradar

# 或者安装后使用命令
pip install -e .
trendradar
```

## 依赖选择

根据你的需求选择合适的安装方式：

| 功能 | 依赖文件 | 安装命令 |
|------|----------|----------|
| 仅核心功能 | requirements-core.txt | pip install -r requirements-core.txt |
| + 云存储 | requirements-storage.txt | pip install -r requirements-core.txt requirements-storage.txt |
| + MCP 服务 | requirements-mcp.txt | pip install -r requirements-core.txt requirements-mcp.txt |
| + 开发工具 | requirements-dev.txt | pip install -r requirements-dev.txt |
| 完整功能 | requirements-all.txt | pip install -r requirements-all.txt |

## 配置

### 最小配置（可选）

无需配置文件，使用默认设置即可。

### 完整配置（可选）

创建 `config/config.yaml`:

```yaml
PLATFORMS:
  - id: zhihu
    name: 知乎
  - id: weibo
    name: 微博

STORAGE:
  BACKEND: local
  DATA_DIR: output
```

创建 `config/frequency_words.txt`:

```
人工智能
AI
科技
```

## 测试

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest

# 查看覆盖率
pytest --cov=trendradar --cov-report=html
```

## 文档

- [API 集成指南](API_README.md) - 详细的 API 使用说明
- [主项目文档](README.md) - 完整的项目文档
- [测试说明](tests/README.md) - 测试相关说明

## 下一步

- 查看 [examples/simple_usage.py](examples/simple_usage.py) 了解更多使用示例
- 阅读 [API_README.md](API_README.md) 了解完整的 API 参考
- 探索 [config/config.yaml](config/config.yaml) 了解配置选项

## 常见问题

**Q: 最小依赖是什么？**

A: 核心依赖包括 requests, pytz, PyYAML, feedparser。

**Q: 如何只抓取新闻不分析？**

A: 直接调用 `api.fetch_news()` 即可。

**Q: 数据存储在哪里？**

A: 默认存储在 `output` 目录的 SQLite 数据库中。

**Q: 需要安装所有依赖吗？**

A: 不需要。根据你的需求选择核心依赖或可选依赖。
