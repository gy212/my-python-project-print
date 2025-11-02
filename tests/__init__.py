#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
键盘输入测试套件

这个包包含了用于测试键盘输入模拟程序准确性的所有测试脚本。

主要模块：
- test_framework: 测试框架核心
- content_diff_tests: 内容差异检测测试
- newline_tests: 换行检测测试
- indentation_tests: 空格缩进检测测试
- run_all_tests: 主测试运行器

使用方法：
    python run_all_tests.py
"""

__version__ = "1.0.0"
__author__ = "Keyboard Typer Test Suite"
__description__ = "键盘输入测试套件 - 检测输入与输出的准确性"

# 导出主要类和函数
from .test_framework import KeyboardTyperTestFramework, TestResult, TextComparisonEngine
from .content_diff_tests import ContentDifferenceTests
from .newline_tests import NewlineTests
from .indentation_tests import IndentationTests

__all__ = [
    'KeyboardTyperTestFramework',
    'TestResult', 
    'TextComparisonEngine',
    'ContentDifferenceTests',
    'NewlineTests',
    'IndentationTests'
]