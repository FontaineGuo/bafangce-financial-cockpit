## 场内基金行情
```python
import akshare as ak

fund_etf_fund_daily_em_df = ak.fund_etf_fund_daily_em()
print(fund_etf_fund_daily_em_df)
```

## 开放式基金实时数据
```python
import akshare as ak

fund_open_fund_daily_em_df = ak.fund_open_fund_daily_em()
print(fund_open_fund_daily_em_df)
```

## 个股信息
```python
import akshare as ak

stock_individual_info_em_df = ak.stock_individual_info_em(symbol="000001")
print(stock_individual_info_em_df)
```
## LOF基金实时行情
```python
import akshare as ak

fund_lof_spot_em_df = ak.fund_lof_spot_em()
print(fund_lof_spot_em_df)
```

## ETF基金实时行情-东财
```python
import akshare as ak

fund_etf_spot_em_df = ak.fund_etf_spot_em()
print(fund_etf_spot_em_df)
```