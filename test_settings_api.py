# 测试/settings API是否正常工作
import requests

# API基本URL
BASE_URL = 'http://localhost:8001'

def test_get_settings():
    """测试获取设置API"""
    print("=== 测试获取设置API ===")
    try:
        response = requests.get(f'{BASE_URL}/settings')
        
        if response.status_code == 200:
            settings = response.json()
            print(f"✓ 获取设置成功")
            print(f"设置内容: {settings}")
            return True
        else:
            print(f"✗ 获取设置失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 获取设置发生异常: {str(e)}")
        return False

def test_update_settings():
    """测试更新设置API"""
    print("\n=== 测试更新设置API ===")
    try:
        # 准备更新的设置数据
        update_data = {
            "settings": {
                "general": {
                    "language": "en-US",
                    "theme": "dark",
                    "auto_sync": False
                },
                "portfolio": {
                    "refresh_interval": 600,  # 10分钟自动刷新
                    "show_real_time": False,
                    "risk_level": "high"
                },
                "notifications": {
                    "enable": True,
                    "threshold": 10.0  # 涨跌幅超过10%时通知
                }
            }
        }
        
        response = requests.put(f'{BASE_URL}/settings', json=update_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 更新设置成功")
            print(f"结果: {result}")
            return True
        else:
            print(f"✗ 更新设置失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 更新设置发生异常: {str(e)}")
        return False

# 主测试函数
def run_tests():
    print("开始测试/settings API...")
    
    # 启动后端服务
    import subprocess
    import time
    import sys
    
    try:
        # 启动后端服务
        server_process = subprocess.Popen([
            sys.executable, '-c', 
            'cd backend && python app.py 8001'
        ], cwd='f:/GitRepos/bafangce-financial-cockpit')
        
        # 等待服务启动
        print("正在启动后端服务...")
        time.sleep(3)  # 等待3秒确保服务启动
        
        # 运行测试
        get_result = test_get_settings()
        update_result = test_update_settings()
        
        # 再次获取设置验证更新
        print("\n=== 再次获取设置验证更新结果 ===")
        test_get_settings()
        
        if get_result and update_result:
            print("\n✅ 所有测试通过！/settings API正常工作")
        else:
            print("\n❌ 测试失败！请检查API实现")
            
    finally:
        # 终止后端服务
        server_process.terminate()
        server_process.wait()
        print("\n后端服务已终止")

if __name__ == "__main__":
    run_tests()
