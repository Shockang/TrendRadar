# 变更日志

## [5.0.0] - 2025-01-02

### 重大变更 ✨

这是 TrendRadar 的重大版本更新，重点改进了作为 Python 库的集成体验。

### 新增功能

#### API 接口
- ✨ 新增 `TrendRadarAPI` 类，提供简化的 Python API
- ✨ 支持 `fetch_news()` - 抓取热点新闻
- ✨ 支持 `analyze_news()` - 分析新闻数据
- ✨ 支持 `filter_by_keywords()` - 关键词过滤
- ✨ 支持 `get_hot_topics()` - 获取热点话题
- ✨ 支持 `get_news_by_date()` - 查询历史数据
- ✨ 支持 `export_html()` - 导出HTML报告

#### 数据模型
- ✨ 新增 `NewsConfig` 配置模型
- ✨ 新增 `NewsItem` 单条新闻模型
- ✨ 新增 `NewsData` 新闻数据集合模型
- ✨ 新增 `TopicStat` 话题统计模型

#### 测试框架
- ✨ 新增完整的单元测试套件
- ✨ 支持单元测试和集成测试分离
- ✨ 添加 pytest 配置文件
- ✨ 支持测试覆盖率报告

#### 依赖管理
- ✨ 分离核心依赖和可选依赖
- ✨ 新增 `requirements-core.txt` - 核心依赖
- ✨ 新增 `requirements-storage.txt` - 云存储依赖
- ✨ 新增 `requirements-mcp.txt` - MCP服务依赖
- ✨ 新增 `requirements-dev.txt` - 开发工具依赖
- ✨ 新增 `requirements-all.txt` - 完整依赖

#### 类型注解
- ✨ 为所有 API 方法添加完整的类型注解
- ✨ 支持 mypy 类型检查
- ✨ 提升代码可维护性

#### 文档
- ✨ 新增 `API_README.md` - API集成指南
- ✨ 新增 `QUICKSTART.md` - 快速开始指南
- ✨ 新增 `tests/README.md` - 测试说明
- ✨ 更新 `SHARED_TASK_NOTES.md` - 项目进度跟踪

### 改进

#### 依赖优化
- 🎨 优化 setup.py，支持按需安装可选依赖
- 🎨 boto3 改为可选依赖（云存储功能）
- 🎨 fastmcp 和 websockets 改为可选依赖（MCP服务）
- 🎨 最小安装只需 4 个核心依赖

#### 代码质量
- 🎨 添加完整的类型注解
- 🎨 改进错误处理
- 🎨 提升代码可测试性

### 安装方式

#### 最小化安装（仅核心功能）
```bash
pip install -r requirements-core.txt
# 或
pip install -e .
```

#### 完整安装（包含所有功能）
```bash
pip install -r requirements-all.txt
# 或
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

### 使用示例

#### 作为 Python 库
```python
from trendradar_api import TrendRadarAPI

api = TrendRadarAPI()
news = api.fetch_news()
hot_topics = api.get_hot_topics(top_n=10)
```

#### 运行测试
```bash
# 运行所有测试
pytest

# 生成覆盖率报告
pytest --cov=trendradar --cov-report=html

# 只运行单元测试
pytest -m "not integration"
```

### 兼容性

- ✅ 完全向后兼容原有命令行工具
- ✅ 原有配置文件格式不变
- ✅ 已有数据可以直接使用
- ✅ 可以逐步迁移到API方式

### 文件变更

#### 新增文件
- `trendradar/core/api.py` - 核心API接口
- `trendradar/core/models.py` - 数据模型
- `examples/simple_usage.py` - 使用示例
- `tests/__init__.py` - 测试包
- `tests/test_api.py` - API测试
- `tests/README.md` - 测试说明
- `pytest.ini` - pytest配置
- `API_README.md` - API集成指南
- `QUICKSTART.md` - 快速开始指南
- `requirements-core.txt` - 核心依赖
- `requirements-storage.txt` - 云存储依赖
- `requirements-mcp.txt` - MCP依赖
- `requirements-dev.txt` - 开发依赖
- `requirements-all.txt` - 完整依赖
- `CHANGELOG.md` - 变更日志（本文件）

#### 修改文件
- `setup.py` - 更新依赖配置，支持extras_require
- `API_README.md` - 添加测试和依赖说明
- `SHARED_TASK_NOTES.md` - 更新项目进度

### 技术债务

#### 已解决
- ✅ 核心API缺少类型注解
- ✅ 缺少单元测试
- ✅ 依赖未分离

#### 待解决
- ⏳ 核心模块以外的类型注解
- ⏳ 提高测试覆盖率到 90%+
- ⏳ 添加 CI/CD 流程
- ⏳ 添加性能基准测试

### 贡献者

- 所有贡献者列表请查看 [GitHub Contributors](https://github.com/sansan0/TrendRadar/graphs/contributors)

### 下一步计划

详见 `SHARED_TASK_NOTES.md` 中的"下一步计划"章节。

---

## 旧版本

详见项目主文档 `README.md`
