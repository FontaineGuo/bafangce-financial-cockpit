import psutil
import os

# 查找占用8000端口的进程
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        connections = proc.info['connections']() if 'connections' in proc.info else []
        for conn in connections:
            if conn.status == 'LISTEN' and conn.laddr.port == 8000:
                print(f"Found process {proc.info['pid']} ({proc.info['name']}) using port 8000")
                os.kill(proc.info['pid'], 9)  # 强制终止
                print(f"Killed process {proc.info['pid']}")
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass

print("Cleanup complete")
