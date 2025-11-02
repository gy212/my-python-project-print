#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主测试运行器
统一执行所有测试脚本：内容差异检测、换行检测、空格缩进检测
"""

import sys
import os
from pathlib import Path
import time
import json
from typing import Dict, List, Any
import argparse
from datetime import datetime

# 添加当前目录和backend目录到路径
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent / "src" / "backend"))

# 导入各个测试模块
try:
    from content_diff_tests import ContentDifferenceTests
    from newline_tests import NewlineTests
    from indentation_tests import IndentationTests
    from test_framework import TestResult
except ImportError as e:
    print(f"导入测试模块失败: {e}")
    print("请确保所有测试脚本都在同一目录下")
    sys.exit(1)


class TestSuite:
    """测试套件主类"""
    
    def __init__(self):
        self.content_tests = ContentDifferenceTests()
        self.newline_tests = NewlineTests()
        self.indentation_tests = IndentationTests()
        
        self.all_results = []
        self.test_summary = {
            'content_diff': {'total': 0, 'passed': 0, 'failed': 0},
            'newline': {'total': 0, 'passed': 0, 'failed': 0},
            'indentation': {'total': 0, 'passed': 0, 'failed': 0}
        }
    
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
    
    def run_content_diff_tests(self, verbose: bool = True):
        """运行内容差异检测测试"""
        if verbose:
            print("=" * 80)
            print("1. 内容差异检测测试")
            print("=" * 80)
        
        try:
            results = self.content_tests.run_all_tests()
            self.all_results.extend(results)
            
            # 统计结果
            self.test_summary['content_diff']['total'] = len(results)
            self.test_summary['content_diff']['passed'] = sum(1 for r in results if r.passed)
            self.test_summary['content_diff']['failed'] = len(results) - self.test_summary['content_diff']['passed']
            
            if verbose:
                print(f"内容差异测试完成: {self.test_summary['content_diff']['passed']}/{self.test_summary['content_diff']['total']} 通过")
            
            return True
        except Exception as e:
            print(f"内容差异测试执行失败: {e}")
            return False
    
    def run_newline_tests(self, verbose: bool = True):
        """运行换行检测测试"""
        if verbose:
            print("\n" + "=" * 80)
            print("2. 换行检测测试")
            print("=" * 80)
        
        try:
            results = self.newline_tests.run_all_tests()
            self.all_results.extend(results)
            
            # 统计结果
            self.test_summary['newline']['total'] = len(results)
            self.test_summary['newline']['passed'] = sum(1 for r in results if r.passed)
            self.test_summary['newline']['failed'] = len(results) - self.test_summary['newline']['passed']
            
            if verbose:
                print(f"换行测试完成: {self.test_summary['newline']['passed']}/{self.test_summary['newline']['total']} 通过")
            
            return True
        except Exception as e:
            print(f"换行测试执行失败: {e}")
            return False
    
    def run_indentation_tests(self, verbose: bool = True):
        """运行空格缩进检测测试"""
        if verbose:
            print("\n" + "=" * 80)
            print("3. 空格缩进检测测试")
            print("=" * 80)
        
        try:
            results = self.indentation_tests.run_all_tests()
            self.all_results.extend(results)
            
            # 统计结果
            self.test_summary['indentation']['total'] = len(results)
            self.test_summary['indentation']['passed'] = sum(1 for r in results if r.passed)
            self.test_summary['indentation']['failed'] = len(results) - self.test_summary['indentation']['passed']
            
            if verbose:
                print(f"缩进测试完成: {self.test_summary['indentation']['passed']}/{self.test_summary['indentation']['total']} 通过")
            
            return True
        except Exception as e:
            print(f"缩进测试执行失败: {e}")
            return False
    
    def run_all_tests(self, test_types: List[str] = None, verbose: bool = True):
        """
        运行所有测试或指定类型的测试
        test_types: 要运行的测试类型列表 ['content', 'newline', 'indentation']
        """
        if test_types is None:
            test_types = ['content', 'newline', 'indentation']
        
        start_time = time.time()
        
        if verbose:
            print("键盘输入测试套件")
            print("=" * 80)
            print("测试目标：")
            print("1. 检测输入与输出在内容上的差异（缺字/多字/错字等）")
            print("2. 检测换行是否正确")
            print("3. 检测空格缩进是否正确")
            print("=" * 80)
        
        success_count = 0
        
        # 运行指定的测试
        if 'content' in test_types:
            if self.run_content_diff_tests(verbose):
                success_count += 1
        
        if 'newline' in test_types:
            if self.run_newline_tests(verbose):
                success_count += 1
        
        if 'indentation' in test_types:
            if self.run_indentation_tests(verbose):
                success_count += 1
        
        total_time = time.time() - start_time
        
        # 生成综合报告
        if verbose:
            self.print_summary_report(total_time)
        
        # 保存报告
        self.save_comprehensive_report(total_time)
        
        return success_count == len(test_types)
    
    def print_summary_report(self, total_time: float):
        """打印总结报告"""
        print("\n" + "=" * 80)
        print("测试总结报告")
        print("=" * 80)
        
        # 各类测试统计
        for test_type, stats in self.test_summary.items():
            if stats['total'] > 0:
                test_name = {
                    'content_diff': '内容差异检测',
                    'newline': '换行检测',
                    'indentation': '空格缩进检测'
                }[test_type]
                
                pass_rate = stats['passed'] / stats['total'] * 100
                print(f"{test_name}:")
                print(f"  总数: {stats['total']}")
                print(f"  通过: {stats['passed']} ({pass_rate:.1f}%)")
                print(f"  失败: {stats['failed']}")
                print()
        
        # 总体统计
        total_tests = sum(stats['total'] for stats in self.test_summary.values())
        total_passed = sum(stats['passed'] for stats in self.test_summary.values())
        total_failed = sum(stats['failed'] for stats in self.test_summary.values())
        
        if total_tests > 0:
            overall_pass_rate = total_passed / total_tests * 100
            print(f"总体统计:")
            print(f"  总测试数: {total_tests}")
            print(f"  总通过数: {total_passed} ({overall_pass_rate:.1f}%)")
            print(f"  总失败数: {total_failed}")
            print(f"  执行时间: {total_time:.3f}秒")
        
        # 失败测试详情
        failed_results = [r for r in self.all_results if not r.passed]
        if failed_results:
            print("\n失败测试详情:")
            print("-" * 60)
            for result in failed_results:
                print(f"测试: {result.test_name}")
                print(f"  差异数量: {len(result.differences)}")
                print(f"  主要问题: {result.summary}")
                
                # 显示前3个差异
                for i, diff in enumerate(result.differences[:3]):
                    print(f"    {i+1}. {diff.description}")
                
                if len(result.differences) > 3:
                    print(f"    ... 还有 {len(result.differences) - 3} 个差异")
                print()
    
    def save_comprehensive_report(self, total_time: float):
        """保存综合报告"""
        # 创建带日期的报告文件夹
        dated_folder = self.create_dated_report_folder()
        
        # 文本报告
        text_report_file = dated_folder / "comprehensive_test_report.txt"
        with open(text_report_file, 'w', encoding='utf-8') as f:
            f.write("键盘输入测试套件 - 综合报告\n")
            f.write("=" * 80 + "\n")
            f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"执行时间: {total_time:.3f}秒\n\n")
            
            # 测试统计
            f.write("测试统计:\n")
            f.write("-" * 40 + "\n")
            for test_type, stats in self.test_summary.items():
                if stats['total'] > 0:
                    test_name = {
                        'content_diff': '内容差异检测',
                        'newline': '换行检测',
                        'indentation': '空格缩进检测'
                    }[test_type]
                    
                    pass_rate = stats['passed'] / stats['total'] * 100
                    f.write(f"{test_name}: {stats['passed']}/{stats['total']} ({pass_rate:.1f}%)\n")
            
            # 详细结果
            f.write("\n详细测试结果:\n")
            f.write("-" * 40 + "\n")
            for result in self.all_results:
                status = "通过" if result.passed else "失败"
                f.write(f"[{status}] {result.test_name}\n")
                if not result.passed:
                    f.write(f"  差异数量: {len(result.differences)}\n")
                    f.write(f"  执行时间: {result.execution_time:.3f}秒\n")
                    for diff in result.differences[:5]:  # 只显示前5个差异
                        f.write(f"    - {diff.description}\n")
                    if len(result.differences) > 5:
                        f.write(f"    ... 还有 {len(result.differences) - 5} 个差异\n")
                f.write("\n")
        
        # JSON报告
        json_report_file = dated_folder / "comprehensive_test_report.json"
        report_data = {
            'metadata': {
                'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'execution_time': total_time,
                'total_tests': len(self.all_results)
            },
            'summary': self.test_summary,
            'results': []
        }
        
        for result in self.all_results:
            result_data = {
                'test_name': result.test_name,
                'passed': result.passed,
                'execution_time': result.execution_time,
                'input_length': len(result.input_text),
                'output_length': len(result.output_text),
                'difference_count': len(result.differences),
                'summary': result.summary,
                'differences': [
                    {
                        'type': diff.type.value,
                        'line_number': diff.line_number,
                        'position': diff.position,
                        'expected': diff.expected,
                        'actual': diff.actual,
                        'description': diff.description
                    }
                    for diff in result.differences
                ]
            }
            report_data['results'].append(result_data)
        
        with open(json_report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n报告已保存:")
        print(f"  文本报告: {text_report_file}")
        print(f"  JSON报告: {json_report_file}")
    
    def run_quick_test(self):
        """运行快速测试（每类测试只运行几个代表性用例）"""
        print("运行快速测试...")
        print("=" * 60)
        
        # 简化的测试用例
        quick_cases = [
            ("基础文本", "Hello World 你好世界"),
            ("换行文本", "第一行\n第二行\n第三行"),
            ("缩进代码", "def hello():\n    print('Hello')\n    return True")
        ]
        
        for name, text in quick_cases:
            print(f"测试: {name}")
            
            # 内容差异测试
            content_result = self.content_tests.framework.run_test(
                test_name=f"快速-内容-{name}",
                input_text=text,
                simulate_typing_func=self.content_tests.simulate_typing_with_errors,
                error_rate=0.0
            )
            
            # 换行测试
            newline_result = self.newline_tests.framework.run_test(
                test_name=f"快速-换行-{name}",
                input_text=text,
                simulate_typing_func=self.newline_tests.simulate_typing_with_newline_errors,
                error_rate=0.0
            )
            
            # 缩进测试
            indent_result = self.indentation_tests.framework.run_test(
                test_name=f"快速-缩进-{name}",
                input_text=text,
                simulate_typing_func=self.indentation_tests.simulate_typing_with_indentation_errors,
                error_rate=0.0
            )
            
            # 显示结果
            results = [content_result, newline_result, indent_result]
            passed = sum(1 for r in results if r.passed)
            print(f"  结果: {passed}/3 通过")
            
            if passed < 3:
                for r in results:
                    if not r.passed:
                        print(f"    失败: {r.test_name} - {len(r.differences)} 个差异")
            print()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='键盘输入测试套件')
    parser.add_argument('--type', '-t', 
                       choices=['content', 'newline', 'indentation', 'all'],
                       default='all',
                       help='要运行的测试类型')
    parser.add_argument('--quick', '-q', 
                       action='store_true',
                       help='运行快速测试')
    parser.add_argument('--verbose', '-v', 
                       action='store_true', 
                       default=True,
                       help='详细输出')
    parser.add_argument('--quiet', 
                       action='store_true',
                       help='静默模式')
    
    args = parser.parse_args()
    
    if args.quiet:
        args.verbose = False
    
    # 创建测试套件
    test_suite = TestSuite()
    
    try:
        if args.quick:
            # 快速测试
            test_suite.run_quick_test()
        else:
            # 完整测试
            if args.type == 'all':
                test_types = ['content', 'newline', 'indentation']
            else:
                test_types = [args.type]
            
            success = test_suite.run_all_tests(test_types, args.verbose)
            
            if success:
                print("\n所有测试执行完成！")
                return 0
            else:
                print("\n部分测试执行失败！")
                return 1
    
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        return 1
    except Exception as e:
        print(f"\n测试执行出错: {e}")
        return 1


if __name__ == "__main__":
    exit(main())