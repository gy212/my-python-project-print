#!/usr/bin/env python3
"""
Keyboard Typer 集成启动器
提供系统检查、快捷方式管理和应用启动功能
"""

import sys
import argparse
from pathlib import Path

# 添加src/backend到路径
sys.path.insert(0, str(Path(__file__).parent / "src" / "backend"))

from system_checker import SystemChecker
from shortcut_manager import ShortcutManager
from start_app import main as start_app_main, parse_arguments as parse_app_args


def print_banner():
    """打印启动横幅"""
    print("=" * 60)
    print("🎯 Keyboard Typer - 智能键盘输入模拟器")
    print("=" * 60)


def check_system():
    """执行系统检查"""
    print("\n🔍 执行系统环境检查...")
    checker = SystemChecker()
    results = checker.run_all_checks()
    
    if results['status'] == 'failed':
        print("\n❌ 系统检查失败，请解决问题后重试")
        print("提示：可以运行 'python launcher.py --fix' 尝试自动修复")
        return False
    elif results['status'] == 'warning':
        print("\n⚠️ 系统检查通过但有警告，建议解决后获得最佳体验")
        return True
    else:
        print("\n✅ 系统检查全部通过！")
        return True


def create_shortcuts():
    """创建快捷方式"""
    print("\n🔗 创建快捷方式...")
    manager = ShortcutManager()
    success = manager.create_all_shortcuts()
    
    if success:
        print("✅ 快捷方式创建成功！")
        print("您现在可以通过以下方式启动应用：")
        print("• 桌面快捷方式")
        print("• 开始菜单 -> 程序 -> Keyboard Typer")
        return True
    else:
        print("❌ 快捷方式创建失败")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Keyboard Typer 集成启动器")
    parser.add_argument("--check", action="store_true", help="只执行系统检查")
    parser.add_argument("--fix", action="store_true", help="尝试修复系统问题")
    parser.add_argument("--shortcuts", action="store_true", help="创建快捷方式")
    parser.add_argument("--remove-shortcuts", action="store_true", help="删除快捷方式")
    parser.add_argument("--dev", action="store_true", help="以开发模式启动应用")
    parser.add_argument("--no-check", action="store_true", help="跳过系统检查直接启动")
    
    args = parser.parse_args()
    
    print_banner()
    
    # 只执行系统检查
    if args.check:
        check_system()
        return
    
    # 修复系统问题
    if args.fix:
        print("\n🔧 尝试修复系统问题...")
        checker = SystemChecker()
        checker.fix_common_issues()
        print("\n" + "="*50)
        check_system()
        return
    
    # 创建快捷方式
    if args.shortcuts:
        create_shortcuts()
        return
    
    # 删除快捷方式
    if args.remove_shortcuts:
        print("\n🗑️ 删除快捷方式...")
        manager = ShortcutManager()
        success = manager.remove_all_shortcuts()
        if success:
            print("✅ 快捷方式删除成功！")
        else:
            print("❌ 快捷方式删除失败")
        return
    
    # 启动应用
    if not args.no_check:
        # 执行系统检查
        if not check_system():
            print("\n💡 提示：如果您想跳过检查直接启动，请使用 --no-check 参数")
            sys.exit(1)
    
    # 询问是否创建快捷方式（仅在首次运行时）
    try:
        manager = ShortcutManager()
        desktop = Path.home() / "Desktop" / f"{manager.app_name}.lnk"
        
        if not desktop.exists():
            print("\n🔗 检测到这是首次运行，是否创建桌面快捷方式？")
            response = input("输入 y/yes 创建，其他键跳过: ").lower().strip()
            if response in ['y', 'yes']:
                create_shortcuts()
    except Exception:
        pass  # 忽略快捷方式检查错误
    
    # 启动应用
    print("\n🚀 启动 Keyboard Typer...")
    
    # 构造start_app的参数
    app_args = []
    if args.dev:
        app_args.append("--dev")
    
    # 模拟命令行参数
    original_argv = sys.argv
    try:
        sys.argv = ["start_app.py"] + app_args
        app_args_parsed = parse_app_args()
        start_app_main(app_args_parsed)
    finally:
        sys.argv = original_argv


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户取消操作")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 启动器出现错误: {e}")
        sys.exit(1)