# Advisor Agent — AGENTS.md

## 工作触发方式

1. **Research A2A 派单**：需要专业数据时
2. **用户直接请求**：需要外汇定价、基金分析时

## 查询处理流

```
收到查询
  │
  ├─ 需要认证 Token？
  │    └─ 从缓存读取 / 刷新 Token
  │
  ├─ 路由判断
  │    ├─ 股票关键词 → Stock Agent API
  │    ├─ 外汇关键词 → FX Agent API
  │    └─ 基金关键词 → Fund Agent API
  │
  └─ 返回结构化结果 → 回传 Research/CIO
```

## API 调用格式

```python
import requests, json

def call_advisor(agent_type: str, query: str, token: str):
    """
    agent_type: 'stock' | 'fx' | 'fund'
    """
    url = f"https://your-advisor-api.com/{agent_type}/query"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(url, json={"query": query}, headers=headers)
    return resp.json()
```

## 降级策略

如果 Advisor API 不可用：
1. 立即通知 CIO："Advisor API 不可用，切换到 yfinance + SearXNG"
2. Research Agent 使用本地数据源继续工作
3. 不阻塞 CIO 的交易决策
