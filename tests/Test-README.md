# 键盘输入测试脚本使用说明

## 概述

本测试套件专门用于检测键盘输入模拟程序的准确性，主要检测以下三个方面：

1. **内容差异检测** - 检测输入与输出在内容上的差异（缺字/多字/错字等）
2. **换行检测** - 检测换行是否正确
3. **空格缩进检测** - 检测空格和缩进是否正确

## 文件结构

```
tests/
├── test_framework.py          # 测试框架核心
├── content_diff_tests.py      # 内容差异检测测试
├── newline_tests.py          # 换行检测测试
├── indentation_tests.py      # 空格缩进检测测试
├── run_all_tests.py          # 主测试运行器
└── README.md                 # 本说明文档
```

## 快速开始

### 1. 运行所有测试

```bash
# 运行完整测试套件
python run_all_tests.py

# 或者使用详细输出
python run_all_tests.py --verbose
```

### 2. 运行特定类型的测试

```bash
# 只运行内容差异检测
python run_all_tests.py --type content

# 只运行换行检测
python run_all_tests.py --type newline

# 只运行空格缩进检测
python run_all_tests.py --type indentation
```

### 3. 快速测试

```bash
# 运行快速测试（每类测试只运行几个代表性用例）
python run_all_tests.py --quick
```

### 4. 静默模式

```bash
# 静默运行，只显示最终结果
python run_all_tests.py --quiet
```

## 详细使用说明

### 主测试运行器 (run_all_tests.py)

这是测试套件的入口点，提供统一的测试执行和报告生成功能。

**命令行参数：**
- `--type, -t`: 指定测试类型 (content/newline/indentation/all)
- `--quick, -q`: 运行快速测试
- `--verbose, -v`: 详细输出（默认开启）
- `--quiet`: 静默模式

**输出文件：**
- `reports/comprehensive_test_report.txt` - 详细的文本报告
- `reports/comprehensive_test_report.json` - 机器可读的JSON报告

### 内容差异检测 (content_diff_tests.py)

检测输入文本与输出文本在字符内容上的差异。

**测试用例包括：**
- 基础文本（英文、中文、混合）
- 特殊字符（标点符号、数字、Unicode字符）
- 长段落文本
- 边界情况（空文本、单字符、重复字符）
- 容易出错的组合

**可单独运行：**
```bash
python content_diff_tests.py
```

**输出文件：**
- `reports/content_diff_test_report.txt`
- `reports/content_diff_test_report.json`

### 换行检测 (newline_tests.py)

检测换行符的正确性和格式。

**测试用例包括：**
- 基础换行测试
- 不同换行格式（LF、CRLF、CR）
- 特殊换行场景（行首行尾换行、纯换行文本）
- 代码格式测试
- 长文本换行测试

**可单独运行：**
```bash
python newline_tests.py
```

**输出文件：**
- `reports/newline_test_report.txt`
- `reports/newline_test_report.json`

### 空格缩进检测 (indentation_tests.py)

检测空格、Tab字符和代码缩进的正确性。

**测试用例包括：**
- 基础空格测试（单个、多个、行首行尾空格）
- Tab字符测试
- 代码缩进测试（Python、JavaScript、HTML等）
- 特殊空格字符（不间断空格、全角空格、零宽空格）
- 缩进一致性检查

**可单独运行：**
```bash
python indentation_tests.py
```

**输出文件：**
- `reports/indentation_test_report.txt`
- `reports/indentation_test_report.json`

## 测试框架 (test_framework.py)

提供核心的测试功能和差异检测引擎。

**主要组件：**
- `TextComparisonEngine` - 文本比较引擎
- `KeyboardTyperTestFramework` - 测试框架主类
- `TestResult` - 测试结果数据结构
- `DifferenceType` - 差异类型枚举

## 错误模拟功能

每个测试脚本都包含错误模拟功能，可以模拟各种输入错误：

### 内容差异错误模拟
- 字符缺失
- 字符重复
- 字符替换
- 字符插入

### 换行错误模拟
- 换行缺失
- 多余换行
- 错误的换行格式

### 缩进错误模拟
- 错误的缩进数量
- 错误的缩进类型（空格/Tab混用）
- 缺少缩进
- 多余缩进

## 报告格式

### 文本报告
包含详细的测试结果、差异统计和失败测试的详细信息。

### JSON报告
机器可读格式，包含：
- 测试元数据
- 统计摘要
- 详细的测试结果
- 每个差异的具体信息

## 自定义测试

### 添加新的测试用例

1. 在相应的测试文件中找到 `_prepare_test_cases` 方法
2. 添加新的测试用例到 `self.test_cases` 列表

```python
self.test_cases.append({
    "name": "自定义测试",
    "input": "测试文本",
    "description": "测试描述"
})
```

### 创建新的测试类型

1. 继承 `KeyboardTyperTestFramework`
2. 实现自定义的错误模拟函数
3. 添加到主测试运行器中

## 性能考虑

- 完整测试套件可能需要几分钟时间
- 使用 `--quick` 参数进行快速验证
- 大文本测试会消耗更多时间和内存
- 错误模拟测试比完美输入测试耗时更长

## 故障排除

### 常见问题

1. **导入错误**
   - 确保所有测试文件在同一目录下
   - 检查Python路径设置

2. **权限错误**
   - 确保有写入报告文件的权限
   - 检查目录访问权限

3. **内存不足**
   - 减少大文本测试用例
   - 使用 `--quick` 模式

### 调试模式

在测试脚本中设置详细输出：

```python
# 在测试函数中添加
print(f"输入: {repr(input_text)}")
print(f"输出: {repr(output_text)}")
```

## 扩展功能

### 集成到CI/CD

```bash
# 在CI脚本中使用
python run_all_tests.py --quiet
if [ $? -eq 0 ]; then
    echo "所有测试通过"
else
    echo "测试失败"
    exit 1
fi
```

### 定期测试

可以设置定时任务定期运行测试：

```bash
# 每日测试
0 2 * * * cd /path/to/project && python src/backend/run_all_tests.py --quiet
```

## 联系和支持

如果遇到问题或需要添加新功能，请：

1. 检查本文档的故障排除部分
2. 查看生成的错误报告
3. 检查测试日志文件

## 版本历史

- v1.0 - 初始版本，包含基础的三类测试
- 支持内容差异、换行、空格缩进检测
- 提供完整的错误模拟和报告功能