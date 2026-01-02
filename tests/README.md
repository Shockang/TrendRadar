# TrendRadar 测试说明

本目录包含 TrendRadar 项目的所有测试代码。

## 测试结构

```
tests/
├── __init__.py          # 测试包初始化
├── test_api.py          # API 单元测试和集成测试
└── README.md            # 本文件
```

## 运行测试

### 快速开始

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行所有测试
pytest
```

### 常用命令

```bash
# 详细输出
pytest -v

# 生成覆盖率报告
pytest --cov=trendradar --cov-report=html

# 只运行单元测试（不需要网络）
pytest -m "not integration"

# 只运行集成测试（需要网络）
pytest -m integration

# 运行特定测试文件
pytest tests/test_api.py

# 运行特定测试类
pytest tests/test_api.py::TestTrendRadarAPI

# 运行特定测试方法
pytest tests/test_api.py::TestTrendRadarAPI::test_init_with_defaults

# 显示打印输出
pytest -s
```

## 测试分类

### 单元测试

单元测试不需要网络连接，可以快速运行。主要包括：

- API 初始化测试
- 配置加载测试
- 关键词过滤测试
- 数据转换测试

### 集成测试

集成测试需要网络连接，用于验证完整的功能流程。主要包括：

- 新闻抓取测试
- 数据存储测试
- 完整工作流测试

## 编写测试

### 测试文件命名

- 测试文件以 `test_` 开头
- 测试类以 `Test` 开头
- 测试方法以 `test_` 开头

### 示例

```python
import pytest
from trendradar.core.api import TrendRadarAPI

class TestMyFeature:
    def test_something(self):
        api = TrendRadarAPI()
        result = api.some_method()
        assert result is not None

    @pytest.mark.integration
    def test_integration(self):
        # 需要网络的测试
        api = TrendRadarAPI()
        news = api.fetch_news()
        assert len(news) > 0
```

## Fixtures

测试中使用的 fixtures：

- `temp_dir`: 创建临时目录，测试后自动清理
- `api`: 创建基本的 API 实例
- `api_with_config`: 创建带配置的 API 实例

## 持续集成

测试在以下情况下自动运行：

- 每次提交代码
- 每次 Pull Request
- 每日定时检查

## 覆盖率目标

- 目标覆盖率：> 80%
- 核心模块覆盖率：> 90%

## 问题反馈

如果发现测试问题或有改进建议，请：

1. 提交 Issue 描述问题
2. 创建 Pull Request 修复或改进测试
