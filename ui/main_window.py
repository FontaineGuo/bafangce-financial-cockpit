# 主界面
import tkinter as tk
from tkinter import ttk
from config.constants import WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.setup_ui()
    
    def setup_ui(self):
        """设置界面布局"""
        pass
    
    def load_holdings(self):
        """加载持仓数据"""
        pass
    
    def refresh_data(self):
        """刷新数据"""
        pass
    
    def show_add_dialog(self):
        """显示添加持仓对话框"""
        pass
    
    def show_edit_dialog(self, holding_id):
        """显示编辑持仓对话框"""
        pass
    
    def delete_holding(self, holding_id):
        """删除持仓"""
        pass
