#!/usr/bin/env python3
# coding=utf-8
"""
TrendRadar 安装脚本

用于将 TrendRadar 作为 Python 包安装到系统
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取 README
readme_file = Path(__file__).parent / "API_README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# 读取版本
version_file = Path(__file__).parent / "version"
version = version_file.read_text().strip() if version_file.exists() else "1.0.0"

setup(
    name="trendradar",
    version=version,
    author="TrendRadar",
    description="热点新闻聚合与分析工具 - 简化API版本",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sansan0/TrendRadar",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "requests>=2.32.5,<3.0.0",
        "pytz>=2025.2,<2026.0",
        "PyYAML>=6.0.3,<7.0.0",
        "boto3>=1.35.0,<2.0.0",
        "feedparser>=6.0.0,<7.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
        "mcp": [
            "fastmcp>=2.12.0,<2.14.0",
            "websockets>=13.0,<14.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "trendradar=trendradar.__main__:main",
            "trendradar-api=examples.simple_usage:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
