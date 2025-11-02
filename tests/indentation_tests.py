#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
空格缩进检测测试脚本
专门测试输入与输出在空格和缩进方面的正确性
"""

import sys
import os
from pathlib import Path
import time
import random
import re
from typing import List, Dict, Tuple, Optional

# 添加当前目录和backend目录到路径，以便导入测试框架和backend模块
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent / "src" / "backend"))

from test_framework import KeyboardTyperTestFramework, TestResult


class IndentationTests:
    """空格缩进测试类"""
    
    def __init__(self):
        self.framework = KeyboardTyperTestFramework()
        self.test_cases = []
        self._prepare_test_cases()
    
    def _prepare_test_cases(self):
        """准备空格缩进测试用例"""
        
        # 1. 基础空格测试
        self.test_cases.extend([
            {
                "name": "单个空格",
                "input": "word1 word2",
                "description": "测试单词间的单个空格"
            },
            {
                "name": "多个空格",
                "input": "word1    word2",
                "description": "测试单词间的多个空格"
            },
            {
                "name": "行首空格",
                "input": "    开头有空格",
                "description": "测试行首的空格"
            },
            {
                "name": "行尾空格",
                "input": "结尾有空格    ",
                "description": "测试行尾的空格"
            },
            {
                "name": "只有空格",
                "input": "        ",
                "description": "测试只包含空格的文本"
            }
        ])
        
        # 2. Tab字符测试
        self.test_cases.extend([
            {
                "name": "单个Tab",
                "input": "word1\tword2",
                "description": "测试单词间的Tab字符"
            },
            {
                "name": "多个Tab",
                "input": "word1\t\t\tword2",
                "description": "测试多个Tab字符"
            },
            {
                "name": "行首Tab",
                "input": "\t开头有Tab",
                "description": "测试行首的Tab字符"
            },
            {
                "name": "空格Tab混合",
                "input": "  \t  mixed\t  \t",
                "description": "测试空格和Tab的混合使用"
            }
        ])
        
        # 3. 代码缩进测试（Python风格 - 4空格）
        self.test_cases.extend([
            {
                "name": "Python函数缩进",
                "input": "def hello():\n    print('Hello')\n    return True",
                "description": "测试Python函数的4空格缩进"
            },
            {
                "name": "Python嵌套缩进",
                "input": "if True:\n    for i in range(3):\n        if i > 0:\n            print(i)",
                "description": "测试Python嵌套结构的缩进"
            },
            {
                "name": "Python类定义",
                "input": "class MyClass:\n    def __init__(self):\n        self.value = 0\n    \n    def method(self):\n        return self.value",
                "description": "测试Python类定义的缩进"
            }
        ])
        
        # 4. 代码缩进测试（JavaScript风格 - 2空格）
        self.test_cases.extend([
            {
                "name": "JavaScript函数缩进",
                "input": "function hello() {\n  console.log('Hello');\n  return true;\n}",
                "description": "测试JavaScript函数的2空格缩进"
            },
            {
                "name": "JavaScript对象缩进",
                "input": "const obj = {\n  name: 'test',\n  value: {\n    nested: true,\n    count: 42\n  }\n};",
                "description": "测试JavaScript对象的缩进"
            }
        ])
        
        # 5. HTML/XML缩进测试
        self.test_cases.extend([
            {
                "name": "HTML基础缩进",
                "input": "<html>\n  <head>\n    <title>Test</title>\n  </head>\n  <body>\n    <h1>Hello</h1>\n  </body>\n</html>",
                "description": "测试HTML的基础缩进"
            },
            {
                "name": "HTML嵌套缩进",
                "input": "<div>\n  <ul>\n    <li>\n      <a href='#'>Link</a>\n    </li>\n  </ul>\n</div>",
                "description": "测试HTML嵌套元素的缩进"
            }
        ])
        
        # 6. 特殊空格字符测试
        self.test_cases.extend([
            {
                "name": "不间断空格",
                "input": "word1\u00A0word2",  # Non-breaking space
                "description": "测试不间断空格字符"
            },
            {
                "name": "全角空格",
                "input": "中文\u3000全角空格",  # Ideographic space
                "description": "测试全角空格字符"
            },
            {
                "name": "零宽空格",
                "input": "word1\u200Bword2",  # Zero-width space
                "description": "测试零宽空格字符"
            }
        ])
        
        # 7. 复杂缩进模式
        self.test_cases.extend([
            {
                "name": "混合缩进风格",
                "input": "function test() {\n\tif (true) {\n    \treturn 'mixed';\n\t}\n}",
                "description": "测试混合的缩进风格（Tab和空格混用）"
            },
            {
                "name": "不规则缩进",
                "input": "line1\n   line2\n     line3\n line4",
                "description": "测试不规则的缩进模式"
            }
        ])
    
    def simulate_typing_with_indentation_errors(self, text: str, error_rate: float = 0.0, **kwargs) -> str:
        """
        模拟带有缩进错误的键盘输入
        error_rate: 缩进错误率 (0.0-1.0)
        """
        if error_rate == 0.0:
            return text  # 无错误，直接返回原文本
        
        lines = text.split('\n')
        result_lines = []
        
        for line in lines:
            if random.random() < error_rate and (line.startswith(' ') or line.startswith('\t')):
                # 对有缩进的行进行错误模拟
                content = line.lstrip()
                original_indent = line[:len(line) - len(content)]
                
                error_type = random.choice(['wrong_count', 'wrong_type', 'missing', 'extra'])
                
                if error_type == 'wrong_count':
                    # 错误的缩进数量
                    if original_indent.startswith(' '):
                        # 空格缩进，随机改变数量
                        space_count = len(original_indent)
                        new_count = max(0, space_count + random.randint(-2, 3))
                        new_indent = ' ' * new_count
                    else:
                        # Tab缩进，随机改变数量
                        tab_count = len(original_indent)
                        new_count = max(0, tab_count + random.randint(-1, 2))
                        new_indent = '\t' * new_count
                    result_lines.append(new_indent + content)
                
                elif error_type == 'wrong_type':
                    # 错误的缩进类型（空格变Tab或Tab变空格）
                    if original_indent.startswith(' '):
                        # 空格变Tab
                        space_count = len(original_indent)
                        tab_count = max(1, space_count // 4)
                        new_indent = '\t' * tab_count
                    else:
                        # Tab变空格
                        tab_count = len(original_indent)
                        space_count = tab_count * 4
                        new_indent = ' ' * space_count
                    result_lines.append(new_indent + content)
                
                elif error_type == 'missing':
                    # 缺少缩进
                    result_lines.append(content)
                
                elif error_type == 'extra':
                    # 额外的缩进
                    extra_indent = random.choice(['  ', '\t', '    '])
                    result_lines.append(original_indent + extra_indent + content)
            
            else:
                # 对普通空格进行错误模拟
                if ' ' in line and random.random() < error_rate * 0.5:
                    # 随机改变单词间的空格
                    words = line.split(' ')
                    new_line_parts = []
                    for i, word in enumerate(words):
                        new_line_parts.append(word)
                        if i < len(words) - 1:  # 不是最后一个单词
                            space_error = random.choice(['missing', 'extra', 'wrong_char'])
                            if space_error == 'missing':
                                pass  # 不添加空格
                            elif space_error == 'extra':
                                new_line_parts.append('  ')  # 双空格
                            elif space_error == 'wrong_char':
                                new_line_parts.append('\t')  # 用Tab替代空格
                            else:
                                new_line_parts.append(' ')  # 正常空格
                    result_lines.append(''.join(new_line_parts))
                else:
                    result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    def analyze_indentation_pattern(self, text: str) -> Dict[str, any]:
        """分析文本的缩进模式"""
        lines = text.split('\n')
        analysis = {
            'total_lines': len(lines),
            'indented_lines': 0,
            'space_indented': 0,
            'tab_indented': 0,
            'mixed_indented': 0,
            'max_indent_level': 0,
            'indent_sizes': [],
            'inconsistent_indentation': False
        }
        
        space_indent_sizes = set()
        tab_indent_sizes = set()
        
        for line in lines:
            if line.strip():  # 非空行
                content = line.lstrip()
                indent = line[:len(line) - len(content)]
                
                if indent:
                    analysis['indented_lines'] += 1
                    
                    if ' ' in indent and '\t' in indent:
                        analysis['mixed_indented'] += 1
                    elif indent.startswith(' '):
                        analysis['space_indented'] += 1
                        space_indent_sizes.add(len(indent))
                    elif indent.startswith('\t'):
                        analysis['tab_indented'] += 1
                        tab_indent_sizes.add(len(indent))
                    
                    analysis['max_indent_level'] = max(analysis['max_indent_level'], len(indent))
        
        # 检查缩进一致性
        if len(space_indent_sizes) > 1 or len(tab_indent_sizes) > 1:
            analysis['inconsistent_indentation'] = True
        
        analysis['space_indent_sizes'] = sorted(list(space_indent_sizes))
        analysis['tab_indent_sizes'] = sorted(list(tab_indent_sizes))
        
        return analysis
    
    def run_basic_indentation_tests(self):
        """运行基础缩进测试"""
        print("=" * 60)
        print("运行基础空格缩进测试")
        print("=" * 60)
        
        basic_cases = self.test_cases[:9]  # 前9个基础测试用例
        
        for test_case in basic_cases:
            print(f"测试: {test_case['name']}")
            print(f"输入: {repr(test_case['input'])}")
            
            result = self.framework.run_test(
                test_name=f"基础缩进-{test_case['name']}",
                input_text=test_case['input'],
                simulate_typing_func=self.simulate_typing_with_indentation_errors,
                error_rate=0.0
            )
            
            status = "✓ 通过" if result.passed else "✗ 失败"
            print(f"结果: {status}")
            
            if not result.passed:
                print(f"差异数量: {len(result.differences)}")
                for diff in result.differences:
                    if 'indentation' in diff.type.value.lower() or 'whitespace' in diff.type.value.lower():
                        print(f"  - {diff.description}")
            print()
    
    def run_code_indentation_tests(self):
        """运行代码缩进测试"""
        print("=" * 60)
        print("运行代码缩进测试")
        print("=" * 60)
        
        code_cases = self.test_cases[9:16]  # 代码缩进测试用例
        
        for test_case in code_cases:
            print(f"测试: {test_case['name']}")
            
            # 分析缩进模式
            analysis = self.analyze_indentation_pattern(test_case['input'])
            print(f"缩进分析:")
            print(f"  总行数: {analysis['total_lines']}")
            print(f"  有缩进的行: {analysis['indented_lines']}")
            print(f"  空格缩进: {analysis['space_indented']}")
            print(f"  Tab缩进: {analysis['tab_indented']}")
            print(f"  混合缩进: {analysis['mixed_indented']}")
            print(f"  最大缩进级别: {analysis['max_indent_level']}")
            
            result = self.framework.run_test(
                test_name=f"代码缩进-{test_case['name']}",
                input_text=test_case['input'],
                simulate_typing_func=self.simulate_typing_with_indentation_errors,
                error_rate=0.0
            )
            
            status = "✓ 通过" if result.passed else "✗ 失败"
            print(f"结果: {status}")
            
            if not result.passed:
                print(f"差异数量: {len(result.differences)}")
                for diff in result.differences:
                    print(f"  - 第{diff.line_number}行: {diff.description}")
            print()
    
    def run_special_space_tests(self):
        """运行特殊空格字符测试"""
        print("=" * 60)
        print("运行特殊空格字符测试")
        print("=" * 60)
        
        special_cases = self.test_cases[16:19]  # 特殊空格测试用例
        
        for test_case in special_cases:
            print(f"测试: {test_case['name']}")
            print(f"输入: {repr(test_case['input'])}")
            
            # 显示特殊字符的Unicode编码
            for char in test_case['input']:
                if ord(char) > 127:
                    print(f"  特殊字符: '{char}' (U+{ord(char):04X})")
            
            result = self.framework.run_test(
                test_name=f"特殊空格-{test_case['name']}",
                input_text=test_case['input'],
                simulate_typing_func=self.simulate_typing_with_indentation_errors,
                error_rate=0.0
            )
            
            status = "✓ 通过" if result.passed else "✗ 失败"
            print(f"结果: {status}")
            
            if not result.passed:
                print(f"差异数量: {len(result.differences)}")
                for diff in result.differences:
                    print(f"  - {diff.description}")
            print()
    
    def run_error_simulation_tests(self):
        """运行缩进错误模拟测试"""
        print("=" * 60)
        print("运行缩进错误模拟测试")
        print("=" * 60)
        
        error_rates = [0.2, 0.4]  # 20%, 40% 错误率
        
        # 选择几个代表性的测试用例
        selected_cases = [
            self.test_cases[10],  # Python函数缩进
            self.test_cases[13],  # JavaScript函数缩进
            self.test_cases[15],  # HTML基础缩进
        ]
        
        for error_rate in error_rates:
            print(f"\n--- 缩进错误率: {error_rate*100}% ---")
            
            for test_case in selected_cases:
                print(f"测试: {test_case['name']}")
                
                result = self.framework.run_test(
                    test_name=f"错误模拟({error_rate*100}%)-{test_case['name']}",
                    input_text=test_case['input'],
                    simulate_typing_func=self.simulate_typing_with_indentation_errors,
                    error_rate=error_rate
                )
                
                status = "✓ 通过" if result.passed else "✗ 失败"
                print(f"  结果: {status}")
                if not result.passed:
                    print(f"  差异数量: {len(result.differences)}")
                    print(f"  差异统计: {result.summary}")
                print()
    
    def run_indentation_consistency_check(self):
        """运行缩进一致性检查"""
        print("=" * 60)
        print("运行缩进一致性检查")
        print("=" * 60)
        
        consistency_cases = self.test_cases[19:]  # 复杂缩进模式测试用例
        
        for test_case in consistency_cases:
            print(f"测试: {test_case['name']}")
            
            analysis = self.analyze_indentation_pattern(test_case['input'])
            
            print(f"一致性分析:")
            print(f"  缩进类型一致: {not analysis['inconsistent_indentation']}")
            print(f"  空格缩进大小: {analysis['space_indent_sizes']}")
            print(f"  Tab缩进大小: {analysis['tab_indent_sizes']}")
            print(f"  混合缩进行数: {analysis['mixed_indented']}")
            
            result = self.framework.run_test(
                test_name=f"一致性检查-{test_case['name']}",
                input_text=test_case['input'],
                simulate_typing_func=self.simulate_typing_with_indentation_errors,
                error_rate=0.0
            )
            
            status = "✓ 通过" if result.passed else "✗ 失败"
            print(f"结果: {status}")
            print()
    
    def run_all_tests(self):
        """运行所有缩进测试"""
        print("开始空格缩进检测测试")
        print("测试目标：检测输入与输出在空格和缩进方面的正确性")
        print()
        
        start_time = time.time()
        
        # 运行各类测试
        self.run_basic_indentation_tests()
        self.run_code_indentation_tests()
        self.run_special_space_tests()
        self.run_indentation_consistency_check()
        self.run_error_simulation_tests()
        
        # 生成报告
        total_time = time.time() - start_time
        print("=" * 60)
        print("测试完成，生成报告...")
        print(f"总执行时间: {total_time:.3f}秒")
        
        # 创建带日期的报告文件夹
        dated_folder = self.framework.create_dated_report_folder()
        
        # 保存详细报告
        report_file = dated_folder / "indentation_test_report.txt"
        report_content = self.framework.generate_report(str(report_file))
        
        # 保存JSON报告
        json_report_file = dated_folder / "indentation_test_report.json"
        self.framework.export_json_report(str(json_report_file))
        
        print(f"详细报告已保存到: {report_file}")
        print(f"JSON报告已保存到: {json_report_file}")
        
        return self.framework.test_results


def main():
    """主函数"""
    print("空格缩进检测测试脚本")
    print("=" * 60)
    
    # 创建测试实例
    indentation_tests = IndentationTests()
    
    # 运行所有测试
    results = indentation_tests.run_all_tests()
    
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
                indent_errors = [d for d in result.differences 
                               if 'indentation' in d.type.value.lower() or 'whitespace' in d.type.value.lower()]
                if indent_errors:
                    print(f"  - {result.test_name}: {len(indent_errors)} 个缩进相关差异")


if __name__ == "__main__":
    main()