# KO Agent — AGENTS.md

## 工作触发方式

KO 主要通过两种方式被触发：
1. **CIO A2A 派单**：交易完成后，自动派单沉淀决策
2. **用户直接请求**：需要复盘、整理原则时

## 工作流

```
收到任务
  │
  ├─ 决策日志任务？
  │    └─ 解析交易信息 → 写入 decisions/YYYY-MM-DD-SYMBOL.md
  │
  ├─ 原则更新任务？
  │    └─ 评估是否符合已有原则 → 更新 principles/
  │
  └─ 复盘任务？
       └─ 汇总持仓数据 → 生成复盘报告 → 通知用户
```

## 决策日志命名规范

```
decisions/
├── YYYY-MM-DD-SYMBOL-ACTION.md    # 单笔决策
│   如：2026-04-09-NVDA-BUY.md
└── YYYY-QN-review.md               # 季度复盘
    如：2026-Q2-review.md
```

## A2A 回复规范

完成后：
1. 在 `#know` 频道发更新摘要
2. `sessions_send(agentId="cio", ...)` 通知 CIO
