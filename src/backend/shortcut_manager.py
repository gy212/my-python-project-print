#!/usr/bin/env python3
"""
快捷键启动管理器
用于为安装后的程序创建桌面快捷方式和开始菜单快捷方式
"""

import os
import sys
import winshell
from pathlib import Path
from win32com.client import Dispatch
import argparse


class ShortcutManager:
    """快捷方式管理器"""
    
    def __init__(self):
        self.app_name = "Keyboard Typer"
        self.app_description = "智能键盘输入模拟器"
        
    def get_executable_path(self) -> Path:
        """获取可执行文件路径"""
        if getattr(sys, 'frozen', False):
            # 如果是打包后的exe
            return Path(sys.executable)
        else:
            # 开发环境，返回start_app.py的路径
            return Path(__file__).parent / "start_app.py"
    
    def get_icon_path(self) -> Path:
        """获取图标路径"""
        project_root = Path(__file__).parent.parent.parent
        icon_path = project_root / "assets" / "icons" / "icon.ico"
        
        if icon_path.exists():
            return icon_path
        else:
            # 如果找不到图标，返回None
            return None
    
    def create_desktop_shortcut(self) -> bool:
        """创建桌面快捷方式"""
        try:
            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, f"{self.app_name}.lnk")
            
            # 如果快捷方式已存在，先删除
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
            
            # 创建快捷方式
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            
            executable_path = self.get_executable_path()
            
            if executable_path.suffix == '.py':
                # 开发环境：使用Python解释器运行
                shortcut.Targetpath = sys.executable
                shortcut.Arguments = f'"{executable_path}"'
                shortcut.WorkingDirectory = str(executable_path.parent)
            else:
                # 生产环境：直接运行exe
                shortcut.Targetpath = str(executable_path)
                shortcut.WorkingDirectory = str(executable_path.parent)
            
            shortcut.Description = self.app_description
            
            # 设置图标
            icon_path = self.get_icon_path()
            if icon_path:
                shortcut.IconLocation = str(icon_path)
            
            shortcut.save()
            
            print(f"✓ 桌面快捷方式已创建: {shortcut_path}")
            return True
            
        except Exception as e:
            print(f"✗ 创建桌面快捷方式失败: {e}")
            return False
    
    def create_start_menu_shortcut(self) -> bool:
        """创建开始菜单快捷方式"""
        try:
            # 获取开始菜单程序文件夹
            start_menu = winshell.start_menu()
            app_folder = os.path.join(start_menu, "Programs", self.app_name)
            
            # 创建应用文件夹
            os.makedirs(app_folder, exist_ok=True)
            
            shortcut_path = os.path.join(app_folder, f"{self.app_name}.lnk")
            
            # 如果快捷方式已存在，先删除
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
            
            # 创建快捷方式
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            
            executable_path = self.get_executable_path()
            
            if executable_path.suffix == '.py':
                # 开发环境：使用Python解释器运行
                shortcut.Targetpath = sys.executable
                shortcut.Arguments = f'"{executable_path}"'
                shortcut.WorkingDirectory = str(executable_path.parent)
            else:
                # 生产环境：直接运行exe
                shortcut.Targetpath = str(executable_path)
                shortcut.WorkingDirectory = str(executable_path.parent)
            
            shortcut.Description = self.app_description
            
            # 设置图标
            icon_path = self.get_icon_path()
            if icon_path:
                shortcut.IconLocation = str(icon_path)
            
            shortcut.save()
            
            print(f"✓ 开始菜单快捷方式已创建: {shortcut_path}")
            return True
            
        except Exception as e:
            print(f"✗ 创建开始菜单快捷方式失败: {e}")
            return False
    
    def remove_desktop_shortcut(self) -> bool:
        """删除桌面快捷方式"""
        try:
            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, f"{self.app_name}.lnk")
            
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
                print(f"✓ 桌面快捷方式已删除: {shortcut_path}")
                return True
            else:
                print("桌面快捷方式不存在")
                return True
                
        except Exception as e:
            print(f"✗ 删除桌面快捷方式失败: {e}")
            return False
    
    def remove_start_menu_shortcut(self) -> bool:
        """删除开始菜单快捷方式"""
        try:
            start_menu = winshell.start_menu()
            app_folder = os.path.join(start_menu, "Programs", self.app_name)
            
            if os.path.exists(app_folder):
                import shutil
                shutil.rmtree(app_folder)
                print(f"✓ 开始菜单快捷方式已删除: {app_folder}")
                return True
            else:
                print("开始菜单快捷方式不存在")
                return True
                
        except Exception as e:
            print(f"✗ 删除开始菜单快捷方式失败: {e}")
            return False
    
    def create_all_shortcuts(self) -> bool:
        """创建所有快捷方式"""
        desktop_success = self.create_desktop_shortcut()
        start_menu_success = self.create_start_menu_shortcut()
        
        return desktop_success and start_menu_success
    
    def remove_all_shortcuts(self) -> bool:
        """删除所有快捷方式"""
        desktop_success = self.remove_desktop_shortcut()
        start_menu_success = self.remove_start_menu_shortcut()
        
        return desktop_success and start_menu_success


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Keyboard Typer 快捷方式管理器")
    parser.add_argument("action", choices=["create", "remove", "create-desktop", "create-startmenu", "remove-desktop", "remove-startmenu"],
                       help="要执行的操作")
    
    args = parser.parse_args()
    
    manager = ShortcutManager()
    
    if args.action == "create":
        print("正在创建快捷方式...")
        success = manager.create_all_shortcuts()
        if success:
            print("\n🎉 所有快捷方式创建成功！")
            print(f"您现在可以通过以下方式启动 {manager.app_name}:")
            print("• 桌面快捷方式")
            print("• 开始菜单 -> 程序 -> Keyboard Typer")
        else:
            print("\n❌ 部分快捷方式创建失败")
            
    elif args.action == "remove":
        print("正在删除快捷方式...")
        success = manager.remove_all_shortcuts()
        if success:
            print("\n✓ 所有快捷方式删除成功！")
        else:
            print("\n❌ 部分快捷方式删除失败")
            
    elif args.action == "create-desktop":
        manager.create_desktop_shortcut()
        
    elif args.action == "create-startmenu":
        manager.create_start_menu_shortcut()
        
    elif args.action == "remove-desktop":
        manager.remove_desktop_shortcut()
        
    elif args.action == "remove-startmenu":
        manager.remove_start_menu_shortcut()


if __name__ == "__main__":
    main()