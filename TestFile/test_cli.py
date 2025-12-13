#!/usr/bin/env python3
# CLI交互测试脚本，用于自动化测试CLI的添加、更新和显示持仓功能
import subprocess
import time

# 测试数据
TEST_ETF_CODE = "515080"
TEST_QUANTITY = "1000"
TEST_PURCHASE_PRICE = "1.5453"
TEST_NEW_QUANTITY = "2000"
TEST_NEW_PURCHASE_PRICE = "1.55"

# 模拟用户输入的命令序列
commands = [
    # 1. 添加持仓
    "1",  # 选择添加持仓
    TEST_ETF_CODE,  # 输入ETF代码
    TEST_QUANTITY,  # 输入份额
    TEST_PURCHASE_PRICE,  # 输入成本价
    "y",  # 确认添加
    
    # 2. 查看所有持仓
    "2",  # 选择查看所有持仓
    
    # 3. 更新持仓
    "3",  # 选择更新持仓
    "1",  # 输入持仓ID（假设是1）
    TEST_NEW_QUANTITY,  # 输入新份额
    TEST_NEW_PURCHASE_PRICE,  # 输入新成本价
    "y",  # 确认更新
    
    # 4. 再次查看所有持仓
    "2",  # 选择查看所有持仓
    
    # 5. 退出
    "0"
]

def test_cli():
    """测试CLI的添加、更新和显示持仓功能"""
    print("开始测试CLI功能...")
    
    # 启动CLI程序
    process = subprocess.Popen(
        ["uv", "run", "python", "ui/cli.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd="f:/GitRepos/bafangce-financial-cockpit"
    )
    
    # 等待程序启动
    time.sleep(1)
    
    output = ""
    
    try:
        # 发送命令并读取输出
        for i, cmd in enumerate(commands):
            # 发送命令
            process.stdin.write(cmd + "\n")
            process.stdin.flush()
            
            # 等待命令执行
            time.sleep(2)
            
            # 读取输出
            if process.stdout.peek():
                chunk = process.stdout.read(process.stdout.buffer.length)
                output += chunk
                print(f"命令 {i+1}: {cmd}\n输出: {chunk}\n{'-'*50}")
    except Exception as e:
        print(f"测试过程中出错: {e}")
    finally:
        # 确保程序退出
        process.stdin.close()
        process.wait()
        
        # 收集剩余输出
        if process.stdout:
            output += process.stdout.read()
        if process.stderr:
            output += process.stderr.read()
        
        # 检查测试结果
        print("\n" + "="*50)
        print("测试结果分析:")
        print("="*50)
        
        # 检查是否成功添加持仓
        if "✅ 持仓添加成功！" in output:
            print("✅ 测试通过: 成功添加持仓")
        else:
            print("❌ 测试失败: 未能添加持仓")
        
        # 检查是否成功查看持仓
        if "=== 查看所有持仓 ===" in output and TEST_ETF_CODE in output:
            print("✅ 测试通过: 成功查看持仓")
        else:
            print("❌ 测试失败: 未能查看持仓")
        
        # 检查是否成功更新持仓
        if "✅ 持仓更新成功！" in output:
            print("✅ 测试通过: 成功更新持仓")
        else:
            print("❌ 测试失败: 未能更新持仓")
        
        print("\n完整输出已保存到 cli_test_output.txt")
        
        # 保存输出到文件
        with open("cli_test_output.txt", "w", encoding="utf-8") as f:
            f.write(output)

if __name__ == "__main__":
    test_cli()
