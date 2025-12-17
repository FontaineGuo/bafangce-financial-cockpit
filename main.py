# 主程序入口
import tkinter as tk
from ui.main_window import MainWindow
from backend.core.database import create_tables, add_category_column_to_holdings


def main():
    """主函数"""
    # 初始化数据库
    create_tables()
    # 确保holdings表有category字段（用于现有数据库的迁移）
    add_category_column_to_holdings()
    
    # 创建主窗口
    root = tk.Tk()
    app = MainWindow(root)
    
    # 启动主循环
    root.mainloop()


if __name__ == "__main__":
    main()
