# TOOLS — Advisor 工具参考

## 投顾 API（需要专业 API 凭证）

### 认证流程
```python
import requests

def get_advisor_token():
    """获取 Advisor API 认证 Token"""
    auth_url = "https://your-auth-domain/oauth2/token"
    resp = requests.post(auth_url, data={
        "grant_type": "client_credentials",
        "client_id": "YOUR_CLIENT_ID",
        "client_secret": "YOUR_CLIENT_SECRET"
    })
    return resp.json()["access_token"]
```

### Stock Agent（股票分析）
```python
def query_stock(symbol: str, token: str):
    """查询股票分析数据"""
    url = f"https://your-advisor-api.com/stock/query"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(url, json={"query": f"分析 {symbol}"}, headers=headers)
    return resp.json()
```

### FX Agent（外汇/期权）
```python
def query_fx(pair: str, token: str):
    """查询外汇汇率或期权定价"""
    url = f"https://your-advisor-api.com/fx/query"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(url, json={"query": pair}, headers=headers)
    return resp.json()
    # 支持: Black-Scholes 定价、Greeks、VaR、CVaR
```

### Fund Agent（基金分析）
```python
def query_fund(query: str, token: str):
    """基金筛选与组合优化"""
    url = f"https://your-advisor-api.com/fund/query"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(url, json={"query": query}, headers=headers)
    return resp.json()
    # 支持: 基金推荐、组合优化、Sharpe 比率、风险评估
```

## 降级方案（无专业 API 时）

当 Advisor API 不可用时，使用以下替代方案：

### yfinance 替代
```python
import yfinance as yf

# 获取股票数据
ticker = yf.Ticker("AAPL")
info = ticker.info          # 基本面数据
hist = ticker.history("1y") # 历史价格
```

### 风险指标计算
```python
import numpy as np

def calculate_sharpe(returns, risk_free_rate=0.05):
    """计算 Sharpe 比率"""
    excess_returns = returns - risk_free_rate / 252
    return np.sqrt(252) * excess_returns.mean() / excess_returns.std()

def calculate_var(returns, confidence=0.95):
    """计算 VaR (历史模拟法)"""
    return np.percentile(returns, (1 - confidence) * 100)
```

## A2A 工具

### 回传 CIO/Research
```python
sessions_send(agentId="cio", message="Advisor 分析结果: [摘要]")
```

### 降级通知
```python
# API 不可用时
sessions_send(agentId="cio", message="⚠️ Advisor API 不可用，已切换到 yfinance + 本地计算")
```
