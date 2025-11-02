#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
换行符检测测试脚本
专门测试输入与输出在换行符方面的正确性
"""

import sys
import os
from pathlib import Path
import time
import random
from typing import List, Dict, Tuple

# 添加当前目录和backend目录到路径，以便导入测试框架和backend模块
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent / "src" / "backend"))

from test_framework import KeyboardTyperTestFramework, TestResult


class NewlineTests:
    """换行符测试类"""
    
    def __init__(self):
        self.framework = KeyboardTyperTestFramework()
        self.test_cases = []
        self._prepare_test_cases()
    
    def _prepare_test_cases(self):
        """准备换行符测试用例"""
        
        # 1. 基础换行测试
        self.test_cases.extend([
            {
                "name": "单行文本",
                "input": "这是一行文本",
                "description": "测试单行文本（无换行）"
            },
            {
                "name": "简单换行",
                "input": "第一行\n第二行",
                "description": "测试简单的两行文本"
            },
            {
                "name": "多行文本",
                "input": "第一行\n第二行\n第三行\n第四行",
                "description": "测试多行文本"
            },
            {
                "name": "空行测试",
                "input": "第一行\n\n第三行",
                "description": "测试包含空行的文本"
            },
            {
                "name": "连续空行",
                "input": "第一行\n\n\n第四行",
                "description": "测试连续空行"
            }
        ])
        
        # 2. 不同换行符格式测试
        self.test_cases.extend([
            {
                "name": "Unix换行符(LF)",
                "input": "行1\n行2\n行3",
                "description": "测试Unix风格换行符(\\n)"
            },
            {
                "name": "Windows换行符(CRLF)",
                "input": "行1\r\n行2\r\n行3",
                "description": "测试Windows风格换行符(\\r\\n)"
            },
            {
                "name": "Mac换行符(CR)",
                "input": "行1\r行2\r行3",
                "description": "测试Mac风格换行符(\\r)"
            },
            {
                "name": "混合换行符",
                "input": "行1\n行2\r\n行3\r行4",
                "description": "测试混合换行符格式"
            }
        ])
        
        # 3. 特殊换行情况
        self.test_cases.extend([
            {
                "name": "行首换行",
                "input": "\n开头有换行",
                "description": "测试文本开头的换行符"
            },
            {
                "name": "行尾换行",
                "input": "结尾有换行\n",
                "description": "测试文本结尾的换行符"
            },
            {
                "name": "首尾都有换行",
                "input": "\n中间内容\n",
                "description": "测试首尾都有换行符"
            },
            {
                "name": "只有换行符",
                "input": "\n\n\n",
                "description": "测试只包含换行符的文本"
            }
        ])
        
        # 4. 代码格式测试（针对IDE模式）
        self.test_cases.extend([
            {
                "name": "Python代码格式",
                "input": "def hello():\n    print('Hello World')\n    return True",
                "description": "测试Python代码的换行格式"
            },
            {
                "name": "JavaScript代码格式",
                "input": "function hello() {\n    console.log('Hello World');\n    return true;\n}",
                "description": "测试JavaScript代码的换行格式"
            },
            {
                "name": "HTML代码格式",
                "input": "<html>\n<head>\n    <title>Test</title>\n</head>\n<body>\n    <h1>Hello</h1>\n</body>\n</html>",
                "description": "测试HTML代码的换行格式"
            }
        ])
        
        # 5. 长文本换行测试
        self.test_cases.extend([
            {
                "name": "长段落换行",
                "input": "这是一个很长的段落，用来测试在长文本中的换行符是否能够正确处理。\n这是第二个段落，同样很长，用来验证多个长段落之间的换行符处理。\n这是第三个段落，继续测试换行符的正确性。",
                "description": "测试长段落中的换行符"
            },
            {
                "name": "诗歌格式",
                "input": "春眠不觉晓，\n处处闻啼鸟。\n夜来风雨声，\n花落知多少。",
                "description": "测试诗歌等特殊格式的换行"
            }
        ])
    
    def simulate_typing_with_newline_errors(self, text: str, error_rate: float = 0.0, **kwargs) -> str:
        """
        模拟带有换行符错误的键盘输入
        error_rate: 换行符错误率 (0.0-1.0)
        """
        if error_rate == 0.0:
            return text  # 无错误，直接返回原文本
        
        result = []
        i = 0
        while i < len(text):
            char = text[i]
            
            if char == '\n' and random.random() < error_rate:
                # 随机选择换行符错误类型
                error_type = random.choice(['missing', 'wrong_type', 'extra'])
                
                if error_type == 'missing':
                    # 缺少换行符：跳过换行符，用空格替代
                    result.append(' ')
                elif error_type == 'wrong_type':
                    # 错误的换行符类型
                    wrong_newlines = ['\r\n', '\r', '\n\n']
                    result.append(random.choice(wrong_newlines))
                elif error_type == 'extra':
                    # 额外的换行符
                    result.append('\n\n')
                i += 1
            elif char == '\r' and i + 1 < len(text) and text[i + 1] == '\n':
                # 处理 \r\n 组合
                if random.random() < error_rate:
                    error_type = random.choice(['split', 'wrong_order', 'missing_part'])
                    if error_type == 'split':
                        result.append('\r')
                        result.append(' ')  # 在中间插入空格
                        result.append('\n')
                    elif error_type == 'wrong_order':
                        result.append('\n\r')  # 颠倒顺序
                    elif error_type == 'missing_part':
                        result.append(random.choice(['\r', '\n']))  # 只保留一部分
                else:
                    result.append('\r\n')
                i += 2
            else:
                result.append(char)
                i += 1
        
        return ''.join(result)
    
    def run_basic_newline_tests(self):
        """运行基础换行符测试"""
        print("=" * 60)
        print("运行基础换行符测试")
        print("=" * 60)
        
        basic_cases = self.test_cases[:9]  # 前9个基础测试用例
        
        for test_case in basic_cases:
            print(f"测试: {test_case['name']}")
            print(f"输入: {repr(test_case['input'])}")
            
            result = self.framework.run_test(
                test_name=f"基础换行-{test_case['name']}",
                input_text=test_case['input'],
                simulate_typing_func=self.simulate_typing_with_newline_errors,
                error_rate=0.0
            )
            
            status = "✓ 通过" if result.passed else "✗ 失败"
            print(f"结果: {status}")
            
            if not result.passed:
                print(f"差异数量: {len(result.differences)}")
                for diff in result.differences:
                    if 'newline' in diff.type.value.lower() or 'NEWLINE' in diff.type.name:
                        print(f"  - {diff.description}")
            print()
    
    def run_newline_format_tests(self):
        """运行不同换行符格式测试"""
        print("=" * 60)
        print("运行换行符格式测试")
        print("=" * 60)
        
        format_cases = self.test_cases[5:9]  # 换行符格式测试用例
        
        for test_case in format_cases:
            print(f"测试: {test_case['name']}")
            print(f"输入: {repr(test_case['input'])}")
            
            result = self.framework.run_test(
                test_name=f"格式测试-{test_case['name']}",
                input_text=test_case['input'],
                simulate_typing_func=self.simulate_typing_with_newline_errors,
                error_rate=0.0
            )
            
            status = "✓ 通过" if result.passed else "✗ 失败"
            print(f"结果: {status}")
            
            if not result.passed:
                print(f"差异数量: {len(result.differences)}")
                # 显示换行符相关的差异
                for diff in result.differences:
                    print(f"  - {diff.description}")
            print()
    
    def run_error_simulation_tests(self):
        """运行换行符错误模拟测试"""
        print("=" * 60)
        print("运行换行符错误模拟测试")
        print("=" * 60)
        
        error_rates = [0.1, 0.3, 0.5]  # 10%, 30%, 50% 错误率
        
        # 选择几个代表性的测试用例
        selected_cases = [
            self.test_cases[2],  # 多行文本
            self.test_cases[6],  # Windows换行符
            self.test_cases[13], # Python代码格式
        ]
        
        for error_rate in error_rates:
            print(f"\n--- 换行符错误率: {error_rate*100}% ---")
            
            for test_case in selected_cases:
                print(f"测试: {test_case['name']}")
                
                result = self.framework.run_test(
                    test_name=f"错误模拟({error_rate*100}%)-{test_case['name']}",
                    input_text=test_case['input'],
                    simulate_typing_func=self.simulate_typing_with_newline_errors,
                    error_rate=error_rate
                )
                
                status = "✓ 通过" if result.passed else "✗ 失败"
                print(f"  结果: {status}")
                if not result.passed:
                    print(f"  差异数量: {len(result.differences)}")
                    print(f"  差异统计: {result.summary}")
                print()
    
    def run_code_format_tests(self):
        """运行代码格式换行测试"""
        print("=" * 60)
        print("运行代码格式换行测试")
        print("=" * 60)
        
        code_cases = self.test_cases[13:16]  # 代码格式测试用例
        
        for test_case in code_cases:
            print(f"测试: {test_case['name']}")
            
            # 显示格式化的输入内容
            lines = test_case['input'].split('\n')
            print("输入内容:")
            for i, line in enumerate(lines, 1):
                print(f"  {i:2d}: {repr(line)}")
            
            result = self.framework.run_test(
                test_name=f"代码格式-{test_case['name']}",
                input_text=test_case['input'],
                simulate_typing_func=self.simulate_typing_with_newline_errors,
                error_rate=0.0
            )
            
            status = "✓ 通过" if result.passed else "✗ 失败"
            print(f"结果: {status}")
            
            if not result.passed:
                print(f"差异数量: {len(result.differences)}")
                for diff in result.differences:
                    print(f"  - 第{diff.line_number}行: {diff.description}")
            print()
    
    def analyze_newline_patterns(self, text: str) -> Dict[str, int]:
        """分析文本中的换行符模式"""
        patterns = {
            'total_lines': len(text.split('\n')),
            'lf_count': text.count('\n'),
            'cr_count': text.count('\r'),
            'crlf_count': text.count('\r\n'),
            'empty_lines': 0,
            'trailing_newline': text.endswith('\n') or text.endswith('\r\n') or text.endswith('\r')
        }
        
        # 计算空行数量
        lines = text.split('\n')
        patterns['empty_lines'] = sum(1 for line in lines if line.strip() == '')
        
        return patterns
    
    def run_pattern_analysis_tests(self):
        """运行换行符模式分析测试"""
        print("=" * 60)
        print("运行换行符模式分析")
        print("=" * 60)
        
        for test_case in self.test_cases[:10]:  # 分析前10个测试用例
            print(f"分析: {test_case['name']}")
            
            patterns = self.analyze_newline_patterns(test_case['input'])
            
            print(f"  总行数: {patterns['total_lines']}")
            print(f"  LF(\\n)数量: {patterns['lf_count']}")
            print(f"  CR(\\r)数量: {patterns['cr_count']}")
            print(f"  CRLF(\\r\\n)数量: {patterns['crlf_count']}")
            print(f"  空行数量: {patterns['empty_lines']}")
            print(f"  末尾有换行符: {patterns['trailing_newline']}")
            print()
    
    def run_all_tests(self):
        """运行所有换行符测试"""
        print("开始换行符检测测试")
        print("测试目标：检测输入与输出在换行符方面的正确性")
        print()
        
        start_time = time.time()
        
        # 运行各类测试
        self.run_pattern_analysis_tests()
        self.run_basic_newline_tests()
        self.run_newline_format_tests()
        self.run_code_format_tests()
        self.run_error_simulation_tests()
        
        # 生成报告
        total_time = time.time() - start_time
        print("=" * 60)
        print("测试完成，生成报告...")
        print(f"总执行时间: {total_time:.3f}秒")
        
        # 创建带日期的报告文件夹
        dated_folder = self.framework.create_dated_report_folder()
        
        # 保存详细报告
        report_file = dated_folder / "newline_test_report.txt"
        report_content = self.framework.generate_report(str(report_file))
        
        # 保存JSON报告
        json_report_file = dated_folder / "newline_test_report.json"
        self.framework.export_json_report(str(json_report_file))
        
        print(f"详细报告已保存到: {report_file}")
        print(f"JSON报告已保存到: {json_report_file}")
        
        return self.framework.test_results


def main():
    """主函数"""
    print("换行符检测测试脚本")
    print("=" * 60)
    
    # 创建测试实例
    newline_tests = NewlineTests()
    
    # 运行所有测试
    results = newline_tests.run_all_tests()
    
    # 显示总结
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r.passed)
    failed_tests = total_tests - passed_tests
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"总测试数: {total_tests}")
    print(f"通过: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
    print(f"失败: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
    
    if failed_tests > 0:
        print("\n失败的测试:")
        for result in results:
            if not result.passed:
                newline_errors = [d for d in result.differences 
                                if 'newline' in d.type.value.lower() or 'NEWLINE' in d.type.name]
                if newline_errors:
                    print(f"  - {result.test_name}: {len(newline_errors)} 个换行符相关差异")


if __name__ == "__main__":
    main()