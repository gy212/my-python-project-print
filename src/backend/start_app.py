import argparse
import os
import shutil
import subprocess
import sys
import time
import threading
from pathlib import Path

def resolve_project_root() -> Path:
    # 从 src/backend/ 目录向上两级到达项目根目录
    return Path(__file__).resolve().parent.parent.parent

def ensure_npm_available() -> str:
    npm_path = shutil.which("npm")
    if not npm_path:
        raise RuntimeError("未找到 npm，请先安装 Node.js 并确保 npm 命令在 PATH 中。")
    return npm_path

def install_node_dependencies(npm_path: str, project_root: Path) -> None:
    # node_modules 在 config 目录下
    config_dir = project_root / "config"
    node_modules_dir = config_dir / "node_modules"
    if node_modules_dir.exists():
        return
    print("[INFO] 检测到缺少 node_modules，正在执行 npm install ...")
    try:
        subprocess.run([npm_path, "install"], cwd=config_dir, check=True)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError("npm install 执行失败，请检查网络或 npm 配置。") from exc

def start_flask_backend(project_root: Path) -> subprocess.Popen:
    """启动Flask后端服务器"""
    backend_script = project_root / "src" / "backend" / "backend.py"
    if not backend_script.exists():
        raise RuntimeError(f"未找到后端脚本: {backend_script}")
    
    print("[INFO] 正在启动 Flask 后端服务器...")
    python_executable = sys.executable
    
    # 在新进程中启动Flask后端
    process = subprocess.Popen(
        [python_executable, str(backend_script)],
        cwd=project_root / "src" / "backend",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # 等待后端启动
    print("[INFO] 等待后端服务器启动 (3秒)...")
    time.sleep(3)
    
    if process.poll() is not None:
        stdout, stderr = process.communicate()
        raise RuntimeError(f"后端启动失败:\n{stderr}")
    
    print("[INFO] Flask 后端服务器已启动 (http://localhost:5000)")
    return process

def run_electron_app(npm_path: str, project_root: Path, dev_mode: bool) -> subprocess.Popen:
    env = os.environ.copy()
    env.setdefault("ELECTRON_MIRROR", "https://npmmirror.com/mirrors/electron/")
    if dev_mode:
        env.setdefault("ELECTRON_FORCE_DEVTOOLS", "1")
        command = [npm_path, "run", "dev"]
        print("[INFO] 启动 Electron 应用 (npm run dev)...")
    else:
        command = [npm_path, "start"]
        print("[INFO] 启动 Electron 应用 (npm start)...")

    # 在config目录下运行npm命令
    config_dir = project_root / "config"
    process = subprocess.Popen(command, cwd=config_dir, env=env)
    return process


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="启动 Tactical Keyboard Typer Electron 应用")
    parser.add_argument(
        "--dev",
        action="store_true",
        help="以开发模式运行，自动打开调试工具"
    )
    return parser.parse_args()


def main(args: argparse.Namespace) -> None:
    project_root = resolve_project_root()
    backend_process = None
    electron_process = None
    
    try:
        # 启动Flask后端
        backend_process = start_flask_backend(project_root)
        
        # 安装npm依赖并启动Electron前端
        npm_path = ensure_npm_available()
        install_node_dependencies(npm_path, project_root)
        electron_process = run_electron_app(npm_path, project_root, dev_mode=args.dev)
        
        print("[INFO] 应用已完全启动")
        print("[INFO] 后端服务: http://localhost:5000")
        print("[INFO] 按 Ctrl+C 退出应用\n")
        
        # 等待Electron进程结束
        try:
            electron_process.wait()
        except KeyboardInterrupt:
            print("\n[INFO] 收到中断信号，正在关闭应用...")
            
    except RuntimeError as error:
        print(f"[ERROR] {error}")
        sys.exit(1)
    finally:
        # 清理进程
        if electron_process and electron_process.poll() is None:
            print("[INFO] 正在关闭 Electron 前端...")
            electron_process.terminate()
            try:
                electron_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                electron_process.kill()
        
        if backend_process and backend_process.poll() is None:
            print("[INFO] 正在关闭 Flask 后端...")
            backend_process.terminate()
            try:
                backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                backend_process.kill()
        
        print("[INFO] 应用已完全关闭")


def entrypoint():
    args = parse_arguments()
    main(args)

if __name__ == "__main__":
    entrypoint()
