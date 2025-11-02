#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内容差异检测测试脚本
专门测试输入与输出在内容上的差异：缺字、多字、错字等情况
"""

import sys
import os
from pathlib import Path
import unittest
from typing import Dict, Any
import time
import random
import string

# 添加当前目录和backend目录到路径，以便导入测试框架和backend模块
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent / "src" / "backend"))

from test_framework import KeyboardTyperTestFramework, TestResult


class ContentDifferenceTests:
    """内容差异测试类"""
    
    def __init__(self):
        self.framework = KeyboardTyperTestFramework()
        self.test_cases = []
        self._prepare_test_cases()
    
    def _prepare_test_cases(self):
        """准备测试用例"""
        
        # 1. 基础文本测试用例
        self.test_cases.extend([
            {
                "name": "基础英文文本",
                "input": "Hello World! This is a basic test.",
                "description": "测试基础英文文本输入"
            },
            {
                "name": "基础中文文本", 
                "input": "你好世界！这是一个基础测试。",
                "description": "测试基础中文文本输入"
            },
            {
                "name": "中英文混合",
                "input": "Hello 世界! This is 一个 mixed test 测试.",
                "description": "测试中英文混合文本输入"
            }
        ])
        
        # 2. 特殊字符测试用例
        self.test_cases.extend([
            {
                "name": "标点符号测试",
                "input": "测试标点：！@#￥%……&*（）——+{}|：\"<>？[]\\;',./ ",
                "description": "测试各种标点符号输入"
            },
            {
                "name": "数字符号测试",
                "input": "1234567890 +-*/=()[]{}^%$#@!~`",
                "description": "测试数字和符号输入"
            },
            {
                "name": "Unicode字符测试",
                "input": "测试Unicode: αβγδε ñáéíóú çüöäß 🚀🎉💻",
                "description": "测试Unicode特殊字符"
            }
        ])
        
        # 3. 长文本测试用例
        self.test_cases.extend([
            {
                "name": "长英文段落",
                "input": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                "description": "测试长英文段落输入"
            },
            {
                "name": "长中文段落",
                "input": "这是一个很长的中文段落测试，用来检测在输入大量中文文本时是否会出现缺字、多字或者错字的情况。我们需要确保每一个汉字都能够正确地被输入到目标位置，不会因为输入法切换或者其他原因导致文字丢失或错误。",
                "description": "测试长中文段落输入"
            }
        ])
        
        # 4. 边界情况测试用例
        self.test_cases.extend([
            {
                "name": "空文本",
                "input": "",
                "description": "测试空文本输入"
            },
            {
                "name": "单字符",
                "input": "A",
                "description": "测试单字符输入"
            },
            {
                "name": "单个中文字符",
                "input": "中",
                "description": "测试单个中文字符输入"
            },
            {
                "name": "重复字符",
                "input": "aaaaaaaaaa",
                "description": "测试重复字符输入"
            },
            {
                "name": "重复中文字符",
                "input": "测测测测测测测测测测",
                "description": "测试重复中文字符输入"
            }
        ])
        
        # 5. 容易出错的字符组合
        self.test_cases.extend([
            {
                "name": "相似字符测试",
                "input": "Il1| O0o rn m 6b 5S Z2",
                "description": "测试容易混淆的相似字符"
            },
            {
                "name": "输入法切换测试",
                "input": "Hello你好World世界Test测试",
                "description": "测试频繁的输入法切换"
            },
            {
                "name": "特殊组合字符",
                "input": "(){}[]<>\"\"''``~~--__++==||\\\\//??!!@@##$$%%^^&&**",
                "description": "测试特殊符号组合"
            }
        ])
    
    def simulate_typing_with_errors(self, text: str, error_rate: float = 0.0, **kwargs) -> str:
        """
        模拟带有错误的键盘输入
        error_rate: 错误率 (0.0-1.0)
        """
        if error_rate == 0.0:
            return text  # 无错误，直接返回原文本
        
        result = []
        for i, char in enumerate(text):
            if random.random() < error_rate:
                # 随机选择错误类型
                error_type = random.choice(['missing', 'extra', 'wrong'])
                
                if error_type == 'missing':
                    # 缺字：跳过当前字符
                    continue
                elif error_type == 'extra':
                    # 多字：添加额外字符
                    if char.isalpha():
                        extra_char = random.choice(string.ascii_letters)
                    elif char.isdigit():
                        extra_char = random.choice(string.digits)
                    else:
                        extra_char = random.choice('!@#$%^&*()')
                    result.append(extra_char)
                    result.append(char)
                elif error_type == 'wrong':
                    # 错字：替换为错误字符
                    if char.isalpha():
                        wrong_char = random.choice(string.ascii_letters)
                    elif char.isdigit():
                        wrong_char = random.choice(string.digits)
                    elif char == ' ':
                        wrong_char = random.choice(['\t', '  '])  # 空格错误
                    else:
                        wrong_char = random.choice('!@#$%^&*()')
                    result.append(wrong_char)
            else:
                result.append(char)
        
        return ''.join(result)
    
    def run_perfect_input_tests(self):
        """运行完美输入测试（无错误）"""
        print("=" * 60)
        print("运行完美输入测试（基准测试）")
        print("=" * 60)
        
        for test_case in self.test_cases:
            print(f"测试: {test_case['name']}")
            
            result = self.framework.run_test(
                test_name=f"完美输入-{test_case['name']}",
                input_text=test_case['input'],
                simulate_typing_func=self.simulate_typing_with_errors,
                error_rate=0.0
            )
            
            status = "✓ 通过" if result.passed else "✗ 失败"
            print(f"  结果: {status}")
            if not result.passed:
                print(f"  差异数量: {len(result.differences)}")
                for diff in result.differences[:3]:  # 只显示前3个差异
                    print(f"    - {diff.description}")
            print()
    
    def run_error_simulation_tests(self):
        """运行错误模拟测试"""
        print("=" * 60)
        print("运行错误模拟测试")
        print("=" * 60)
        
        error_rates = [0.05, 0.1, 0.2]  # 5%, 10%, 20% 错误率
        
        for error_rate in error_rates:
            print(f"\n--- 错误率: {error_rate*100}% ---")
            
            # 选择几个代表性的测试用例
            selected_cases = [
                self.test_cases[1],  # 基础中文文本
                self.test_cases[2],  # 中英文混合
                self.test_cases[7],  # 输入法切换测试
            ]
            
            for test_case in selected_cases:
                print(f"测试: {test_case['name']}")
                
                result = self.framework.run_test(
                    test_name=f"错误模拟({error_rate*100}%)-{test_case['name']}",
                    input_text=test_case['input'],
                    simulate_typing_func=self.simulate_typing_with_errors,
                    error_rate=error_rate
                )
                
                status = "✓ 通过" if result.passed else "✗ 失败"
                print(f"  结果: {status}")
                if not result.passed:
                    print(f"  差异数量: {len(result.differences)}")
                    print(f"  差异统计: {result.summary}")
                print()
    
    def run_stress_tests(self):
        """运行压力测试"""
        print("=" * 60)
        print("运行压力测试")
        print("=" * 60)
        
        # 生成大量随机文本进行测试
        stress_cases = [
            {
                "name": "大量英文文本",
                "input": ' '.join([''.join(random.choices(string.ascii_letters, k=random.randint(3, 10))) 
                                 for _ in range(100)]),
                "description": "测试大量随机英文单词"
            },
            {
                "name": "大量数字文本",
                "input": ' '.join([''.join(random.choices(string.digits, k=random.randint(3, 8))) 
                                 for _ in range(50)]),
                "description": "测试大量随机数字"
            },
            {
                "name": "混合字符压力测试",
                "input": ''.join(random.choices(string.ascii_letters + string.digits + '!@#$%^&*()', k=500)),
                "description": "测试500个随机混合字符"
            }
        ]
        
        for test_case in stress_cases:
            print(f"测试: {test_case['name']}")
            print(f"文本长度: {len(test_case['input'])} 字符")
            
            result = self.framework.run_test(
                test_name=f"压力测试-{test_case['name']}",
                input_text=test_case['input'],
                simulate_typing_func=self.simulate_typing_with_errors,
                error_rate=0.0
            )
            
            status = "✓ 通过" if result.passed else "✗ 失败"
            print(f"  结果: {status}")
            print(f"  执行时间: {result.execution_time:.3f}秒")
            if not result.passed:
                print(f"  差异数量: {len(result.differences)}")
            print()
    
    def run_all_tests(self):
        """运行所有内容差异测试"""
        print("开始内容差异检测测试")
        print("测试目标：检测输入与输出在内容上的差异（缺字/多字/错字）")
        print()
        
        start_time = time.time()
        
        # 运行各类测试
        self.run_perfect_input_tests()
        self.run_error_simulation_tests()
        self.run_stress_tests()
        
        # 生成报告
        total_time = time.time() - start_time
        print("=" * 60)
        print("测试完成，生成报告...")
        print(f"总执行时间: {total_time:.3f}秒")
        # 创建带日期的报告文件夹
        dated_folder = self.framework.create_dated_report_folder()
        
        # 保存详细报告
        report_file = dated_folder / "content_diff_test_report.txt"
        report_content = self.framework.generate_report(str(report_file))
        
        # 保存JSON报告
        json_report_file = dated_folder / "content_diff_test_report.json"
        self.framework.export_json_report(str(json_report_file))
        
        print(f"详细报告已保存到: {report_file}")
        print(f"JSON报告已保存到: {json_report_file}")
        
        return self.framework.test_results


def main():
    """主函数"""
    print("内容差异检测测试脚本")
    print("=" * 60)
    
    # 创建测试实例
    content_tests = ContentDifferenceTests()
    
    # 运行所有测试
    results = content_tests.run_all_tests()
    
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
                print(f"  - {result.test_name}: {len(result.differences)} 个差异")


if __name__ == "__main__":
    main()