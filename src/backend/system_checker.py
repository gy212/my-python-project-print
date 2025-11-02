#!/usr/bin/env python3
"""
系统自动检查模块
用于检查系统环境、依赖项、配置等是否正常
"""

import os
import sys
import subprocess
import platform
import shutil
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import importlib.util


class SystemChecker:
    """系统检查器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = 0
        
    def log_success(self, message: str):
        """记录成功信息"""
        print(f"✓ {message}")
        self.checks_passed += 1
        
    def log_error(self, message: str):
        """记录错误信息"""
        print(f"✗ {message}")
        self.checks_failed += 1
        
    def log_warning(self, message: str):
        """记录警告信息"""
        print(f"⚠ {message}")
        self.warnings += 1
        
    def check_python_version(self) -> bool:
        """检查Python版本"""
        print("\n🔍 检查Python环境...")
        
        version = sys.version_info
        if version.major == 3 and version.minor >= 8:
            self.log_success(f"Python版本: {version.major}.{version.minor}.{version.micro}")
            return True
        else:
            self.log_error(f"Python版本过低: {version.major}.{version.minor}.{version.micro} (需要 >= 3.8)")
            return False
    
    def check_virtual_environment(self) -> bool:
        """检查虚拟环境"""
        venv_path = self.project_root / ".venv"
        
        if venv_path.exists():
            self.log_success(f"虚拟环境存在: {venv_path}")
            
            # 检查虚拟环境中的Python
            if platform.system() == "Windows":
                venv_python = venv_path / "Scripts" / "python.exe"
            else:
                venv_python = venv_path / "bin" / "python"
                
            if venv_python.exists():
                self.log_success("虚拟环境Python可执行文件存在")
                return True
            else:
                self.log_error("虚拟环境Python可执行文件不存在")
                return False
        else:
            self.log_warning("虚拟环境不存在，建议创建虚拟环境")
            return True  # 不是致命错误
    
    def check_dependencies(self) -> bool:
        """检查Python依赖项"""
        print("\n🔍 检查Python依赖项...")
        
        requirements_file = self.project_root / "config" / "requirements.txt"
        
        if not requirements_file.exists():
            self.log_error(f"requirements.txt文件不存在: {requirements_file}")
            return False
            
        self.log_success(f"requirements.txt文件存在: {requirements_file}")
        
        # 读取依赖项
        try:
            with open(requirements_file, 'r', encoding='utf-8') as f:
                requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        except Exception as e:
            self.log_error(f"读取requirements.txt失败: {e}")
            return False
        
        # 检查每个依赖项
        all_installed = True
        for requirement in requirements:
            package_name = requirement.split('==')[0].split('>=')[0].split('<=')[0]
            
            # 特殊处理一些包名映射
            import_name = package_name
            if package_name == 'flask-cors':
                import_name = 'flask_cors'
            elif package_name == 'pywin32':
                import_name = 'win32api'  # pywin32的一个主要模块
            
            try:
                importlib.import_module(import_name)
                self.log_success(f"依赖项已安装: {package_name}")
            except ImportError:
                self.log_error(f"依赖项未安装: {package_name}")
                all_installed = False
        
        return all_installed
    
    def check_nodejs_npm(self) -> bool:
        """检查Node.js和npm"""
        print("\n🔍 检查Node.js环境...")
        
        # 检查Node.js
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip()
                self.log_success(f"Node.js版本: {version}")
            else:
                self.log_error("Node.js未安装或不在PATH中")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.log_error("Node.js未安装或不在PATH中")
            return False
        
        # 检查npm
        try:
            # 在Windows上，npm可能是npm.cmd
            npm_cmd = 'npm.cmd' if platform.system() == 'Windows' else 'npm'
            result = subprocess.run([npm_cmd, '--version'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip()
                self.log_success(f"npm版本: {version}")
                return True
            else:
                # 尝试使用npm（不带.cmd）
                result = subprocess.run(['npm', '--version'], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    version = result.stdout.strip()
                    self.log_success(f"npm版本: {version}")
                    return True
                else:
                    self.log_error("npm未安装或不在PATH中")
                    return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.log_error("npm未安装或不在PATH中")
            return False
    
    def check_node_modules(self) -> bool:
        """检查Node.js依赖项"""
        print("\n🔍 检查Node.js依赖项...")
        
        config_dir = self.project_root / "config"
        node_modules = config_dir / "node_modules"
        package_json = config_dir / "package.json"
        
        if not package_json.exists():
            self.log_error(f"package.json文件不存在: {package_json}")
            return False
            
        self.log_success(f"package.json文件存在: {package_json}")
        
        if node_modules.exists():
            self.log_success(f"node_modules目录存在: {node_modules}")
            
            # 检查关键依赖
            electron_path = node_modules / "electron"
            if electron_path.exists():
                self.log_success("Electron已安装")
                return True
            else:
                self.log_warning("Electron未安装，需要运行npm install")
                return False
        else:
            self.log_warning(f"node_modules目录不存在，需要运行npm install")
            return False
    
    def check_project_structure(self) -> bool:
        """检查项目结构"""
        print("\n🔍 检查项目结构...")
        
        required_files = [
            "src/backend/backend.py",
            "src/backend/start_app.py",
            "src/backend/main.js",
            "src/frontend/ui.html",
            "config/package.json",
            "config/requirements.txt"
        ]
        
        all_exist = True
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.log_success(f"文件存在: {file_path}")
            else:
                self.log_error(f"文件缺失: {file_path}")
                all_exist = False
        
        return all_exist
    
    def check_assets(self) -> bool:
        """检查资源文件"""
        print("\n🔍 检查资源文件...")
        
        assets_dir = self.project_root / "assets"
        if not assets_dir.exists():
            self.log_warning("assets目录不存在")
            return True  # 不是致命错误
        
        # 检查图标文件
        icon_files = [
            "assets/icons/icon.ico",
            "assets/icons/icon.svg"
        ]
        
        for icon_path in icon_files:
            full_path = self.project_root / icon_path
            if full_path.exists():
                self.log_success(f"图标文件存在: {icon_path}")
            else:
                self.log_warning(f"图标文件缺失: {icon_path}")
        
        return True
    
    def check_ports(self) -> bool:
        """检查端口占用"""
        print("\n🔍 检查端口占用...")
        
        import socket
        
        # 检查Flask后端端口 (5000)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                result = s.connect_ex(('localhost', 5000))
                if result == 0:
                    self.log_warning("端口5000已被占用，可能影响后端启动")
                else:
                    self.log_success("端口5000可用")
        except Exception as e:
            self.log_warning(f"检查端口5000时出错: {e}")
        
        return True
    
    def check_permissions(self) -> bool:
        """检查文件权限"""
        print("\n🔍 检查文件权限...")
        
        # 检查项目目录写权限
        try:
            test_file = self.project_root / "test_write_permission.tmp"
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            self.log_success("项目目录具有写权限")
            return True
        except Exception as e:
            self.log_error(f"项目目录缺少写权限: {e}")
            return False
    
    def run_all_checks(self) -> Dict:
        """运行所有检查"""
        print("🚀 开始系统环境检查...\n")
        
        results = {
            'python_version': self.check_python_version(),
            'virtual_environment': self.check_virtual_environment(),
            'dependencies': self.check_dependencies(),
            'nodejs_npm': self.check_nodejs_npm(),
            'node_modules': self.check_node_modules(),
            'project_structure': self.check_project_structure(),
            'assets': self.check_assets(),
            'ports': self.check_ports(),
            'permissions': self.check_permissions()
        }
        
        # 统计结果
        print(f"\n📊 检查结果统计:")
        print(f"✓ 通过: {self.checks_passed}")
        print(f"✗ 失败: {self.checks_failed}")
        print(f"⚠ 警告: {self.warnings}")
        
        # 判断整体状态
        critical_checks = ['python_version', 'dependencies', 'nodejs_npm', 'project_structure', 'permissions']
        critical_failed = [check for check in critical_checks if not results[check]]
        
        if critical_failed:
            print(f"\n❌ 系统检查失败！关键问题: {', '.join(critical_failed)}")
            print("请解决上述问题后重新运行检查。")
            return {'status': 'failed', 'results': results, 'critical_issues': critical_failed}
        elif self.warnings > 0:
            print(f"\n⚠️ 系统检查通过，但有 {self.warnings} 个警告")
            print("建议解决警告问题以获得最佳体验。")
            return {'status': 'warning', 'results': results, 'warnings': self.warnings}
        else:
            print(f"\n🎉 系统检查全部通过！环境配置正常。")
            return {'status': 'success', 'results': results}
    
    def fix_common_issues(self) -> bool:
        """尝试修复常见问题"""
        print("\n🔧 尝试修复常见问题...")
        
        fixed_issues = 0
        
        # 尝试安装Python依赖
        try:
            requirements_file = self.project_root / "config" / "requirements.txt"
            if requirements_file.exists():
                print("正在安装Python依赖...")
                result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)], 
                                      capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    self.log_success("Python依赖安装成功")
                    fixed_issues += 1
                else:
                    self.log_error(f"Python依赖安装失败: {result.stderr}")
        except Exception as e:
            self.log_error(f"安装Python依赖时出错: {e}")
        
        # 尝试安装Node.js依赖
        try:
            config_dir = self.project_root / "config"
            if (config_dir / "package.json").exists():
                print("正在安装Node.js依赖...")
                result = subprocess.run(['npm', 'install'], cwd=config_dir, 
                                      capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    self.log_success("Node.js依赖安装成功")
                    fixed_issues += 1
                else:
                    self.log_error(f"Node.js依赖安装失败: {result.stderr}")
        except Exception as e:
            self.log_error(f"安装Node.js依赖时出错: {e}")
        
        if fixed_issues > 0:
            print(f"\n✓ 修复了 {fixed_issues} 个问题")
            return True
        else:
            print("\n⚠ 没有找到可以自动修复的问题")
            return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Keyboard Typer 系统检查工具")
    parser.add_argument("--fix", action="store_true", help="尝试自动修复常见问题")
    parser.add_argument("--json", action="store_true", help="以JSON格式输出结果")
    
    args = parser.parse_args()
    
    checker = SystemChecker()
    
    if args.fix:
        checker.fix_common_issues()
        print("\n" + "="*50)
    
    results = checker.run_all_checks()
    
    if args.json:
        print("\n" + json.dumps(results, indent=2, ensure_ascii=False))
    
    # 返回适当的退出码
    if results['status'] == 'failed':
        sys.exit(1)
    elif results['status'] == 'warning':
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()