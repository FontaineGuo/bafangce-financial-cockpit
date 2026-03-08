"""
八方策金融座舱 - 启动脚本

快速启动前端和后端开发服务器
"""
import os
import sys
import subprocess
import time
from pathlib import Path

# 颜色输出
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_colored(text, color):
    """打印彩色文本"""
    print(f"{color}{text}{Colors.ENDC}")

def print_header(text):
    """打印标题"""
    print_colored(f"\n{'='*60}", Colors.HEADER)
    print_colored(f"  {text}", Colors.HEADER)
    print_colored(f"{'='*60}\n", Colors.HEADER)

def print_success(text):
    """打印成功信息"""
    print_colored(f"✓ {text}", Colors.OKGREEN)

def print_info(text):
    """打印信息"""
    print_colored(f"ℹ {text}", Colors.OKCYAN)

def print_warning(text):
    """打印警告"""
    print_colored(f"⚠ {text}", Colors.WARNING)

def print_error(text):
    """打印错误"""
    print_colored(f"✗ {text}", Colors.FAIL)

def check_dependencies():
    """检查依赖项"""
    print_header("检查依赖项")

    dependencies = {
        'node': 'Node.js (前端需要)',
        'npm': 'npm (前端包管理器)',
        'uv': 'uv (Python 包管理器)'
    }

    missing = []
    for cmd, desc in dependencies.items():
        try:
            subprocess.run([cmd, '--version'], capture_output=True, check=True)
            print_success(f"{desc} 已安装")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print_error(f"{desc} 未安装")
            missing.append(desc)

    if missing:
        print_error("\n请先安装缺失的依赖项：")
        for dep in missing:
            print(f"  - {dep}")
        sys.exit(1)

def check_frontend_deps():
    """检查前端依赖"""
    print_header("检查前端依赖")

    frontend_dir = Path("frontend")
    node_modules = frontend_dir / "node_modules"

    if not node_modules.exists():
        print_warning("前端依赖未安装，正在安装...")
        try:
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
            print_success("前端依赖安装完成")
        except subprocess.CalledProcessError:
            print_error("前端依赖安装失败")
            return False
    else:
        print_success("前端依赖已安装")

    return True

def check_backend_deps():
    """检查后端依赖"""
    print_header("检查后端依赖")

    backend_dir = Path("backend")

    # 检查 uv 配置文件
    uv_lock = backend_dir / "uv.lock"
    if not uv_lock.exists():
        print_error("后端 uv.lock 文件不存在")
        return False

    print_success("后端 uv 配置文件存在")

    # 检查 uv 命令是否可用
    try:
        subprocess.run(["uv", "--version"], capture_output=True, check=True)
        print_success("uv 包管理器已安装")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("uv 包管理器未安装")
        print_info("请安装 uv: pip install uv")
        return False

    # 检查依赖是否已安装
    try:
        result = subprocess.run(
            ["uv", "run", "python", "-c", "import akshare"],
            cwd=backend_dir,
            capture_output=True,
            check=True,
            text=True
        )
        print_success("后端依赖已安装")
    except subprocess.CalledProcessError:
        print_warning("后端依赖未完全安装，正在同步...")
        try:
            subprocess.run(["uv", "sync"], cwd=backend_dir, check=True)
            print_success("后端依赖同步完成")
        except subprocess.CalledProcessError:
            print_error("后端依赖同步失败")
            return False

    return True

def start_backend():
    """启动后端服务器"""
    backend_dir = Path("backend")

    print_header("启动后端服务器")
    print_info("后端服务器将在 http://localhost:8000 启动")
    print_info("API文档: http://localhost:8000/docs\n")

    return subprocess.Popen(
        ["uv", "run", "python", "run.py"],
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

def start_frontend():
    """启动前端开发服务器"""
    frontend_dir = Path("frontend")

    print_header("启动前端开发服务器")
    print_info("前端服务器将在 http://localhost:5173 启动\n")

    return subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

def wait_for_servers(backend_proc, frontend_proc):
    """等待服务器启动"""
    print_header("等待服务器启动...")

    # 等待5秒让服务器启动
    for i in range(5):
        time.sleep(1)
        print_info(f"启动中... {5-i}秒")

    # 检查进程状态
    backend_running = backend_proc.poll() is None
    frontend_running = frontend_proc.poll() is None

    if backend_running and frontend_running:
        print_success("\n所有服务器启动成功！")
        print_info("前端: http://localhost:5173")
        print_info("后端: http://localhost:8000")
        print_info("API文档: http://localhost:8000/docs")
        print_colored("\n按 Ctrl+C 停止所有服务器", Colors.WARNING)
        return True
    else:
        print_error("\n服务器启动失败！")
        if not backend_running:
            print_error("后端服务器启动失败")
        if not frontend_running:
            print_error("前端服务器启动失败")
        return False

def monitor_servers(backend_proc, frontend_proc):
    """监控服务器状态"""
    try:
        while True:
            time.sleep(1)

            # 检查进程状态
            if backend_proc.poll() is not None:
                print_error("后端服务器已停止")
                break

            if frontend_proc.poll() is not None:
                print_error("前端服务器已停止")
                break

    except KeyboardInterrupt:
        print_info("\n正在停止所有服务器...")

        # 终止进程
        backend_proc.terminate()
        frontend_proc.terminate()

        # 等待进程结束
        try:
            backend_proc.wait(timeout=5)
            frontend_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend_proc.kill()
            frontend_proc.kill()

        print_success("所有服务器已停止")

def cleanup():
    """清理端口占用"""
    print_header("清理端口占用")

    backend_dir = Path("backend")
    kill_script = backend_dir / "kill_server.py"

    if kill_script.exists():
        try:
            subprocess.run(
                ["uv", "run", "python", str(kill_script)],
                cwd=backend_dir,
                check=True
            )
            print_success("端口清理完成")
        except subprocess.CalledProcessError:
            print_warning("端口清理失败，可能需要手动清理")
    else:
        print_info("端口清理脚本不存在")

def main():
    """主函数"""
    print_header("八方策金融座舱 - 启动脚本")

    # 检查系统依赖
    check_dependencies()

    # 检查项目依赖
    if not check_frontend_deps():
        return

    if not check_backend_deps():
        return

    # 清理端口占用
    cleanup()

    # 启动服务器
    backend_proc = start_backend()
    frontend_proc = start_frontend()

    # 等待服务器启动
    if not wait_for_servers(backend_proc, frontend_proc):
        # 如果启动失败，终止进程
        backend_proc.terminate()
        frontend_proc.terminate()
        return

    # 监控服务器
    monitor_servers(backend_proc, frontend_proc)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print_error(f"发生错误: {e}")
        sys.exit(1)