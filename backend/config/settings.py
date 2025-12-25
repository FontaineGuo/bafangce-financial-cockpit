# 配置文件管理
import json
import os

# 设置文件路径
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "settings.json")

# 默认设置
DEFAULT_SETTINGS = {
    "general": {
        "language": "zh-CN",
        "theme": "light",
        "auto_sync": True
    },
    "portfolio": {
        "refresh_interval": 300,  # 5分钟自动刷新
        "show_real_time": True,
        "risk_level": "medium"
    },
    "notifications": {
        "enable": True,
        "threshold": 5.0  # 涨跌幅超过5%时通知
    }
}


def load_settings():
    """加载配置文件"""
    try:
        # 如果设置文件不存在，创建默认设置文件
        if not os.path.exists(SETTINGS_FILE):
            save_settings(DEFAULT_SETTINGS)
            return DEFAULT_SETTINGS
        
        # 读取设置文件
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            settings = json.load(f)
        
        return settings
    except Exception as e:
        print(f"加载设置文件失败: {str(e)}")
        return DEFAULT_SETTINGS


def save_settings(settings):
    """保存配置文件"""
    try:
        # 确保配置文件目录存在
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        
        # 保存设置到文件
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"保存设置文件失败: {str(e)}")
        return False


def get_setting(key, default=None):
    """获取指定配置项"""
    try:
        settings = load_settings()
        
        # 支持点号分隔的键路径，如 "general.language"
        keys = key.split(".")
        value = settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    except Exception as e:
        print(f"获取配置项失败: {str(e)}")
        return default


def set_setting(key, value):
    """设置指定配置项"""
    try:
        settings = load_settings()
        
        # 支持点号分隔的键路径，如 "general.language"
        keys = key.split(".")
        current = settings
        
        # 导航到最后一个键的父级
        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]
        
        # 设置值
        current[keys[-1]] = value
        
        # 保存更新后的设置
        return save_settings(settings)
    except Exception as e:
        print(f"设置配置项失败: {str(e)}")
        return False
