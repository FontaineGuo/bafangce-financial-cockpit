# 主程序入口
import tkinter as tk
from ui.main_window import MainWindow
from core.database import create_tables


def main():
    """主函数"""
    # 初始化数据库
    create_tables()
    
    # 创建主窗口
    root = tk.Tk()
    app = MainWindow(root)
    
    # 启动主循环
    root.mainloop()


if __name__ == "__main__":
    main()
