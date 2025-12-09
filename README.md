## 八方策金融座舱


1. 项目概述
一个用于个人投资管理的Python工具，通过akshare获取金融产品实时数据，并计算持仓成本与现值的桌面应用。

2. 技术栈选择
核心语言: Python 3.14+
数据获取: akshare
数据存储: SQLite（轻量级，适合个人使用）
界面框架: 暂未确定，先使用Tkinter
数据处理: pandas
配置文件: JSON/YAML

3. 项目结构建议
bafangce-finacial-cockpit/
├── main.py              # 主程序入口
├── config/
│   ├── __init__.py
│   ├── settings.py      # 配置文件管理
│   └── constants.py     # 常量定义
├── core/
│   ├── __init__.py
│   ├── data_fetcher.py  # 数据获取模块
│   ├── portfolio.py     # 持仓管理模块
│   ├── calculator.py    # 计算模块
│   └── database.py      # 数据库操作
├── ui/
│   ├── __init__.py
│   ├── main_window.py   # 主界面
│   ├── add_dialog.py    # 添加持仓对话框
│   └── edit_dialog.py   # 编辑持仓对话框
├── models/
│   ├── __init__.py
│   ├── holding.py       # 持仓数据模型
│   └── product.py       # 金融产品模型（暂未使用，未来用于存储金融产品基本资料）
├── utils/
│   ├── __init__.py
│   ├── validators.py    # 输入验证
│   └── helpers.py       # 辅助函数
├── data/
│   └── portfolio.db     # SQLite数据库文件
└── pyproject.toml     # uv配置文件
