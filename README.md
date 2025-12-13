## 八方策金融座舱


1. 项目概述
一个用于个人投资管理的Python工具，通过akshare获取金融产品实时数据，并计算持仓成本与现值的桌面应用。支持CLI界面和HTML报表导出功能。

2. 技术栈选择
核心语言: Python 3.14+
数据获取: akshare
数据存储: SQLite（轻量级，适合个人使用）
界面框架: Tkinter（GUI） + CLI界面
数据处理: pandas
配置文件: JSON/YAML
依赖管理: uv

3. 项目结构
bafangce-financial-cockpit/
├── main.py              # 主程序入口
├── config/
│   ├── __init__.py
│   ├── settings.py      # 配置文件管理
│   └── constants.py     # 常量定义
├── core/
│   ├── __init__.py
│   ├── data_fetcher.py  # 数据获取模块
│   ├── holdings_manager.py     # 持仓管理模块
│   ├── calculator.py    # 计算模块
│   └── database.py      # 数据库操作
├── ui/
│   ├── __init__.py
│   ├── main_window.py   # GUI主界面
│   ├── add_dialog.py    # 添加持仓对话框
│   ├── edit_dialog.py   # 编辑持仓对话框
│   └── cli.py           # 命令行界面
├── models/
│   ├── __init__.py
│   ├── holding.py       # 持仓数据模型
│   └── product.py       # 金融产品模型
├── utils/
│   ├── __init__.py
│   ├── validators.py    # 输入验证
│   ├── helpers.py       # 辅助函数
│   └── html_exporter.py # HTML报表导出工具
├── .gitignore           # Git忽略文件
├── .python-version      # Python版本管理
├── LICENSE              # 开源许可证
├── pyproject.toml       # uv配置文件
└── uv.lock              # 依赖锁定文件
