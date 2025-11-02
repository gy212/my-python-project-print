#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
键盘输入测试框架
用于检测输入与输出在内容、换行、空格缩进等方面的差异
"""

import unittest
import difflib
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import json
import time
from pathlib import Path
from datetime import datetime


class DifferenceType(Enum):
    """差异类型枚举"""
    MISSING_CHAR = "缺字"
    EXTRA_CHAR = "多字"
    WRONG_CHAR = "错字"
    NEWLINE_ERROR = "换行错误"
    INDENTATION_ERROR = "缩进错误"
    WHITESPACE_ERROR = "空格错误"


@dataclass
class TestDifference:
    """测试差异数据类"""
    type: DifferenceType
    position: int
    line_number: int
    column: int
    expected: str
    actual: str
    description: str


@dataclass
class TestResult:
    """测试结果数据类"""
    test_name: str
    passed: bool
    differences: List[TestDifference]
    input_text: str
    output_text: str
    execution_time: float
    summary: Dict[str, int]


class TextComparisonEngine:
    """文本比较引擎"""
    
    def __init__(self):
        self.differences = []
    
    def compare_texts(self, expected: str, actual: str) -> List[TestDifference]:
        """比较两个文本，返回差异列表"""
        self.differences = []
        
        # 1. 基础字符差异检测
        self._detect_character_differences(expected, actual)
        
        # 2. 换行符检测
        self._detect_newline_differences(expected, actual)
        
        # 3. 缩进和空格检测
        self._detect_indentation_differences(expected, actual)
        
        return self.differences
    
    def _detect_character_differences(self, expected: str, actual: str):
        """检测字符级别的差异"""
        matcher = difflib.SequenceMatcher(None, expected, actual)
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'delete':
                # 缺字
                missing_text = expected[i1:i2]
                line_num, col = self._get_position_info(expected, i1)
                self.differences.append(TestDifference(
                    type=DifferenceType.MISSING_CHAR,
                    position=i1,
                    line_number=line_num,
                    column=col,
                    expected=missing_text,
                    actual="",
                    description=f"位置 {i1} 缺少字符: '{missing_text}'"
                ))
            
            elif tag == 'insert':
                # 多字
                extra_text = actual[j1:j2]
                line_num, col = self._get_position_info(actual, j1)
                self.differences.append(TestDifference(
                    type=DifferenceType.EXTRA_CHAR,
                    position=j1,
                    line_number=line_num,
                    column=col,
                    expected="",
                    actual=extra_text,
                    description=f"位置 {j1} 多出字符: '{extra_text}'"
                ))
            
            elif tag == 'replace':
                # 错字
                expected_text = expected[i1:i2]
                actual_text = actual[j1:j2]
                line_num, col = self._get_position_info(expected, i1)
                self.differences.append(TestDifference(
                    type=DifferenceType.WRONG_CHAR,
                    position=i1,
                    line_number=line_num,
                    column=col,
                    expected=expected_text,
                    actual=actual_text,
                    description=f"位置 {i1} 字符错误: 期望 '{expected_text}', 实际 '{actual_text}'"
                ))
    
    def _detect_newline_differences(self, expected: str, actual: str):
        """检测换行符差异"""
        expected_lines = expected.splitlines(keepends=True)
        actual_lines = actual.splitlines(keepends=True)
        
        # 检查行数差异
        if len(expected_lines) != len(actual_lines):
            self.differences.append(TestDifference(
                type=DifferenceType.NEWLINE_ERROR,
                position=0,
                line_number=0,
                column=0,
                expected=f"{len(expected_lines)} 行",
                actual=f"{len(actual_lines)} 行",
                description=f"行数不匹配: 期望 {len(expected_lines)} 行, 实际 {len(actual_lines)} 行"
            ))
        
        # 检查每行的换行符
        for i, (exp_line, act_line) in enumerate(zip(expected_lines, actual_lines)):
            exp_ending = self._get_line_ending(exp_line)
            act_ending = self._get_line_ending(act_line)
            
            if exp_ending != act_ending:
                self.differences.append(TestDifference(
                    type=DifferenceType.NEWLINE_ERROR,
                    position=len(''.join(expected_lines[:i])) + len(exp_line.rstrip()),
                    line_number=i + 1,
                    column=len(exp_line.rstrip()),
                    expected=repr(exp_ending),
                    actual=repr(act_ending),
                    description=f"第 {i+1} 行换行符不匹配: 期望 {repr(exp_ending)}, 实际 {repr(act_ending)}"
                ))
    
    def _detect_indentation_differences(self, expected: str, actual: str):
        """检测缩进差异"""
        expected_lines = expected.splitlines()
        actual_lines = actual.splitlines()
        
        for i, (exp_line, act_line) in enumerate(zip(expected_lines, actual_lines)):
            exp_indent = self._get_indentation(exp_line)
            act_indent = self._get_indentation(act_line)
            
            if exp_indent != act_indent:
                self.differences.append(TestDifference(
                    type=DifferenceType.INDENTATION_ERROR,
                    position=len('\n'.join(expected_lines[:i])) + (1 if i > 0 else 0),
                    line_number=i + 1,
                    column=0,
                    expected=repr(exp_indent),
                    actual=repr(act_indent),
                    description=f"第 {i+1} 行缩进不匹配: 期望 {repr(exp_indent)}, 实际 {repr(act_indent)}"
                ))
    
    def _get_position_info(self, text: str, position: int) -> Tuple[int, int]:
        """获取位置的行号和列号"""
        lines = text[:position].split('\n')
        line_number = len(lines)
        column = len(lines[-1]) if lines else 0
        return line_number, column
    
    def _get_line_ending(self, line: str) -> str:
        """获取行的结束符"""
        if line.endswith('\r\n'):
            return '\r\n'
        elif line.endswith('\n'):
            return '\n'
        elif line.endswith('\r'):
            return '\r'
        return ''
    
    def _get_indentation(self, line: str) -> str:
        """获取行的缩进"""
        return line[:len(line) - len(line.lstrip())]


class KeyboardTyperTestFramework:
    """键盘输入测试框架主类"""
    
    def __init__(self):
        self.comparison_engine = TextComparisonEngine()
        self.test_results = []
    
    def create_dated_report_folder(self, base_path: str = "reports") -> Path:
        """创建带日期时间戳的报告文件夹"""
        # 生成时间戳格式: YYYY-MM-DD_HH-MM-SS
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # 创建完整路径
        base_dir = Path(__file__).parent / base_path
        dated_folder = base_dir / timestamp
        
        # 创建文件夹（如果不存在）
        dated_folder.mkdir(parents=True, exist_ok=True)
        
        return dated_folder
    
    def run_test(self, test_name: str, input_text: str, simulate_typing_func, **kwargs) -> TestResult:
        """运行单个测试"""
        start_time = time.time()
        
        try:
            # 模拟键盘输入过程
            output_text = simulate_typing_func(input_text, **kwargs)
            
            # 比较输入输出
            differences = self.comparison_engine.compare_texts(input_text, output_text)
            
            # 生成测试结果
            passed = len(differences) == 0
            execution_time = time.time() - start_time
            
            # 统计差异类型
            summary = {}
            for diff in differences:
                diff_type = diff.type.value
                summary[diff_type] = summary.get(diff_type, 0) + 1
            
            result = TestResult(
                test_name=test_name,
                passed=passed,
                differences=differences,
                input_text=input_text,
                output_text=output_text,
                execution_time=execution_time,
                summary=summary
            )
            
            self.test_results.append(result)
            return result
            
        except Exception as e:
            # 处理测试异常
            result = TestResult(
                test_name=test_name,
                passed=False,
                differences=[TestDifference(
                    type=DifferenceType.WRONG_CHAR,
                    position=0,
                    line_number=0,
                    column=0,
                    expected=input_text,
                    actual=f"ERROR: {str(e)}",
                    description=f"测试执行异常: {str(e)}"
                )],
                input_text=input_text,
                output_text="",
                execution_time=time.time() - start_time,
                summary={"执行异常": 1}
            )
            
            self.test_results.append(result)
            return result
    
    def generate_report(self, output_file: Optional[str] = None) -> str:
        """生成测试报告"""
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("键盘输入测试报告")
        report_lines.append("=" * 80)
        report_lines.append(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"总测试数: {len(self.test_results)}")
        
        passed_count = sum(1 for result in self.test_results if result.passed)
        report_lines.append(f"通过测试: {passed_count}")
        report_lines.append(f"失败测试: {len(self.test_results) - passed_count}")
        report_lines.append("")
        
        # 详细测试结果
        for i, result in enumerate(self.test_results, 1):
            report_lines.append(f"{i}. 测试: {result.test_name}")
            report_lines.append(f"   状态: {'✓ 通过' if result.passed else '✗ 失败'}")
            report_lines.append(f"   执行时间: {result.execution_time:.3f}秒")
            
            if result.differences:
                report_lines.append(f"   发现 {len(result.differences)} 个差异:")
                for diff in result.differences:
                    report_lines.append(f"     - {diff.description}")
            
            if result.summary:
                report_lines.append(f"   差异统计: {result.summary}")
            
            report_lines.append("")
        
        report_content = "\n".join(report_lines)
        
        if output_file:
            Path(output_file).write_text(report_content, encoding='utf-8')
        
        return report_content
    
    def export_json_report(self, output_file: str):
        """导出JSON格式的测试报告"""
        report_data = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "total_tests": len(self.test_results),
            "passed_tests": sum(1 for result in self.test_results if result.passed),
            "failed_tests": sum(1 for result in self.test_results if not result.passed),
            "results": []
        }
        
        for result in self.test_results:
            result_data = {
                "test_name": result.test_name,
                "passed": result.passed,
                "execution_time": result.execution_time,
                "summary": result.summary,
                "differences": [
                    {
                        "type": diff.type.value,
                        "position": diff.position,
                        "line_number": diff.line_number,
                        "column": diff.column,
                        "expected": diff.expected,
                        "actual": diff.actual,
                        "description": diff.description
                    }
                    for diff in result.differences
                ]
            }
            report_data["results"].append(result_data)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # 测试框架示例
    framework = KeyboardTyperTestFramework()
    
    def mock_typing_function(text: str, **kwargs) -> str:
        """模拟键盘输入函数（用于测试框架本身）"""
        return text  # 简单返回原文本
    
    # 运行示例测试
    result = framework.run_test(
        "基础文本测试",
        "Hello World\nThis is a test.",
        mock_typing_function
    )
    
    print(framework.generate_report())