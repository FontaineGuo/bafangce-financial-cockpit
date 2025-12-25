# 测试baostock登录状态缓存机制
from datetime import date
from backend.utils.helpers import is_trading_day

# 获取今天的日期
today = date.today()

print("第一次调用is_trading_day：")
result1 = is_trading_day(today)
print(f"结果: {result1}")

print("\n第二次调用is_trading_day：")
result2 = is_trading_day(today)
print(f"结果: {result2}")

print("\n第三次调用is_trading_day：")
result3 = is_trading_day(today)
print(f"结果: {result3}")
