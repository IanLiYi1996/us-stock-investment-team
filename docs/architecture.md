# 系统架构详解

## 整体架构

```
┌──────────────────────────────────────────────────────────────┐
│                        用户 (User)                            │
│         通过 Slack 频道与各 Agent 交互                         │
└──────────────────────────┬───────────────────────────────────┘
                           │ 请求 / 策略调整
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                      CIO Agent                               │
│                   (#invest-us-market)                        │
│                                                              │
│  • 交易执行（Alpaca Paper Trading API）                        │
│  • 盘中持仓监控（每30min自动巡检）                              │
│  • 自动止损止盈（分级触发）                                     │
│  • 决策验证（收到 Research 报告后核实）                         │
│  • 异常预警（thesis 变化时主动提醒）                            │
└──────┬──────────────────────────────────┬────────────────────┘
       │ A2A 派单（sessions_spawn）         │ A2A 派单
       │ 调研任务                           │ 知识沉淀
       ▼                                   ▼
┌──────────────────┐             ┌─────────────────────┐
│  Research Agent  │             │      KO Agent        │
│   (#research)    │             │      (#know)         │
│                  │             │                      │
│ • 新闻聚合调研    │             │ • 决策日志维护        │
│ • 财务数据分析    │             │ • 投资原则更新        │
│ • 多源交叉验证    │             │ • 周/月/季复盘        │
│ • 标的筛选打分    │             │ • 知识库索引          │
└────────┬─────────┘             └─────────────────────┘
         │ 专业查询
         ▼
┌──────────────────────────────────────────────────────────────┐
│                      Advisor Agent                           │
│                                                              │
│  Stock Agent: 实时行情、技术指标、分析师评级                    │
│  FX Agent:    外汇汇率、期权定价、风险度量                      │
│  Fund Agent:  基金筛选、组合优化、风险评估                      │
└──────────────────────────────────────────────────────────────┘
```

## 技术栈

| 层 | 组件 | 说明 |
|----|------|------|
| Agent 框架 | [OpenClaw](https://openclaw.ai) | 多 Agent 编排、Slack 集成 |
| 交易执行 | [Alpaca](https://alpaca.markets) | Paper Trading API |
| 市场数据 | yfinance | 美股行情、基本面数据 |
| A股/宏观 | akshare | A股、期货、宏观经济数据 |
| 搜索引擎 | SearXNG (Docker) | 本地部署，聚合多引擎 |
| 备用搜索 | Tavily API | 深度搜索，含 AI 摘要 |
| 通信 | Slack | Agent 间协作、用户通知 |

## 数据流

### 调研驱动型交易

```
1. CIO 发现标的 或 用户提出候选标的
2. CIO → sessions_spawn(research) 派单
3. Research 执行：
   a. 多源新闻聚合（RSS + 搜索）
   b. 财务数据分析（yfinance）
   c. 技术面分析（RSI/MACD/均线）
   d. 多源交叉验证
4. Research → CIO 回传结构化报告
5. CIO 验证数据 + 评估风险
6. CIO 执行交易（Alpaca API）
7. CIO → sessions_spawn(ko) 记录决策
8. KO 更新 decisions/ + principles/
```

### 自动监控型交易

```
trading_monitor.py 每 5 分钟运行：
1. 获取所有持仓的当前盈亏
2. 检查是否触发止盈/止损阈值
3. 自动执行卖出（Alpaca 市价单）
4. 在 #invest-us-market 频道通知用户
5. 记录交易日志
```

### 盘前事件扫描

```
pre_market_scan.py（UTC 12:00/13:00 运行）：
1. 扫描隔夜重大新闻（Tavily + RSS）
2. 对持仓标的逐一情绪分类
3. 生成 signals/pre-market-signals.json
4. CIO 读取信号，决定开盘调仓策略
```

## Slack 频道架构

```
#invest-us-market  — CIO 主频道（交易通知、持仓更新）
#research          — Research 调研报告
#know              — KO 知识更新
#advisor           — Advisor 投顾数据（可选）
```

## Agent 间通信协议

详见 [shared/A2A_PROTOCOL.md](../shared/A2A_PROTOCOL.md)

**核心原则：**
1. 跨 Agent 调用 = Slack 可见锚点 + sessions_spawn 触发
2. 结果回传 = sessions_send + Slack 频道可见消息
3. 所有操作可追溯（Slack 线程 = 任务审计日志）
