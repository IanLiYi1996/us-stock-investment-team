# TOOLS — CIO

## Alpaca Paper Trading API

```python
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

# 初始化（使用 ~/.alpaca/credentials 文件）
import os
with open(os.path.expanduser('~/.alpaca/credentials')) as f:
    creds = dict(line.strip().split('=',1) for line in f if '=' in line)

client = TradingClient(
    creds['ALPACA_API_KEY'],
    creds['ALPACA_SECRET_KEY'],
    paper=True   # ⚠️ 改为 False 操作真实账户（需用户明确授权）
)

# 获取持仓
positions = client.get_all_positions()

# 市价买入
order = client.submit_order(MarketOrderRequest(
    symbol="AAPL",
    qty=10,
    side=OrderSide.BUY,
    time_in_force=TimeInForce.DAY
))

# 市价卖出
order = client.submit_order(MarketOrderRequest(
    symbol="AAPL",
    qty=5,
    side=OrderSide.SELL,
    time_in_force=TimeInForce.DAY
))

# 获取账户信息
account = client.get_account()
print(f"总资产: ${account.portfolio_value}")
print(f"可用资金: ${account.buying_power}")
```

## yfinance — 实时行情 + 财务数据

```python
import yfinance as yf

ticker = yf.Ticker("AAPL")
info = ticker.info

# 主要指数
indices = {
    "^GSPC": "S&P 500", "^DJI": "道琼斯",
    "^IXIC": "纳斯达克", "^VIX": "VIX 恐惧指数"
}

# 批量获取当日行情
data = yf.download(["AAPL","GOOGL","MSFT"], period="1d", interval="5m")
```

## 本地分析脚本

```bash
# 基本面 + 技术面综合分析
python3 scripts/stock_analysis.py AAPL NVDA TSM

# 盘前事件扫描
python3 scripts/pre_market_scan.py

# 盘中止损止盈监控
python3 scripts/trading_monitor.py
```

## 搜索引擎（用于信息验证）

```bash
# SearXNG 本地搜索（推荐）
curl -s "http://localhost:8888/search?q=AAPL+earnings&format=json" | \
  python3 -c "import sys,json; [print(r['title'],r['url']) for r in json.load(sys.stdin)['results'][:5]]"

# Tavily API（备用）
curl -s -X POST "https://api.tavily.com/search" \
  -H "Content-Type: application/json" \
  -d '{"api_key":"YOUR_TAVILY_KEY","query":"AAPL news","max_results":5}'
```
