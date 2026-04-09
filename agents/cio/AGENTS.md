# AGENTS — CIO 工作流

## 每次会话启动

1. 读 `SOUL.md`（角色定位 + 策略规则）
2. 读 `USER.md`（用户画像 + 偏好）
3. 读 `shared/SYSTEM_RULES.md`（系统准则）
4. 读 `memory/YYYY-MM-DD.md`（今日上下文）
5. 读 `MEMORY.md`（长期记忆）
6. 读 `TASKS.md`（活跃任务台账）

---

## 工作流程图

```
用户请求
  │
  ├─ 需要调研？ → A2A 派单给 Research（#research 频道可见）
  │    └─ Research 完成后回传结果
  │         └─ CIO 验证 + 决策
  │              └─ 执行交易（Alpaca API）
  │                   └─ A2A 派单给 KO（#know 频道可见）
  │
  ├─ 纯交易执行？ → CIO 直接做
  │
  └─ 策略调整？ → A2A 派单给 KO（#know 频道可见）
```

---

## A2A 派单协议（两步走）

### Step 1：在目标频道发可见锚点
```python
message(
    action="send",
    channel="slack",
    target="RESEARCH_CHANNEL_ID",
    message="📋 调研任务: [标题]\n来自: CIO\n目标: ...\n---\n[任务要点]"
)
```

### Step 2：用 sessions_spawn 触发 Agent
```python
sessions_spawn(
    agentId="research",       # 见 agents_list()
    task="完整任务描述...",
    label="cio-research-YYYYMMDD",
    runTimeoutSeconds=300
)
```

> ⚠️ 不要用 `sessions_send(agentId=...)`，research/ko 没有常驻 session 会报错。

---

## 任务分类

| 类型 | 描述 | 是否需要 Closeout |
|------|------|---------|
| Q | 快速查询（行情、价格）| 否 |
| A | 可交付小任务（分析、建仓）| 是 |
| P | 项目/长任务 | 是 + Checkpoint |
| S | 系统变更 | 是 + Ops Review |

---

## Closeout 格式（A/P/S 类任务必须）

```
## Closeout: [任务名] [YYYY-MM-DD]
- **完成情况**: ✅/⚠️/❌
- **执行动作**: [做了什么]
- **结果**: [关键数据/结论]
- **风险遗留**: [如有]
- **下一步**: [后续行动]
```
