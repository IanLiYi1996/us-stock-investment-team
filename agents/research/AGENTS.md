# AGENTS — Research 工作流

## 每次会话启动

1. 读 `SOUL.md`（角色定位 + 调研原则）
2. 读 `USER.md`（用户画像 + 偏好）
3. 读 `shared/SYSTEM_RULES.md`（系统准则）
4. 读 `MEMORY.md`（长期记忆）
5. 读 `TASKS.md`（活跃任务台账）

---

## 接收 A2A 任务

当 CIO 通过 `sessions_spawn` 派单时，解析任务包并执行：

```
收到任务包
  │
  ├─ 解析：目标 / DoD / 标的 / 时间窗口
  ├─ 制定调研计划（新闻 + 数据 + 验证）
  ├─ 执行调研（多源并行）
  ├─ 交叉验证（至少2源）
  └─ 输出结构化报告 → 回传 CIO
```

## 调研执行步骤

### 1. 新闻层（事件扫描）
```python
# 优先：SearXNG 本地搜索
curl "http://localhost:8888/search?q={symbol}+stock+news&format=json"

# 备用：Tavily
curl -X POST "https://api.tavily.com/search" -d '{"query":"{symbol} latest news"}'

# RSS 源快速扫描（见 TOOLS.md）
```

### 2. 数据层（财务验证）
```python
# 基本面 + 技术面分析
python3 scripts/stock_analysis.py {SYMBOL}
```

### 3. 交叉验证
- 搜索结论来源 ≥ 2 个独立媒体
- 财务数据与 SEC Filing 交叉验证
- 标注每条结论的信息源

### 4. 输出报告（双通道模式）
- 在 #research 频道 thread 发**完整报告**
- sessions_send 回传 CIO **执行摘要**（≤5 行：结论、置信度、首要风险、建议）
- CIO 需要细节时去 #research thread 查看

## 任务超时处理

若 10 分钟内无法完成，发送中间报告：
```
⏳ Research 中间更新
已完成：[已完成部分]
进行中：[正在处理]
预计：X 分钟后完成
```
