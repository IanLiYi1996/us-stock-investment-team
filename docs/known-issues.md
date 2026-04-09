# 已知问题与应对策略

> 记录系统运行中的已知限制和推荐应对方式。严重程度：P0（阻塞）> P1（影响效率）> P2（可接受）

---

## P0: Slack 频道 Session 污染

**现象**：同一频道中多个不相关的 root message 可能共享 session 上下文，导致 Agent 混淆不同任务。

**影响**：Agent 可能将 A 任务的上下文带入 B 任务的回复中。

**应对**：
- 使用简短的 root message 作为锚点，所有详细内容在 thread 中进行
- 避免在频道主线里混聊多个任务
- 一个任务 = 一个 thread = 一个 session

---

## P1: A2A 可见性缺失

**现象**：通过 `sessions_send` 触发目标 Agent 后，目标 Agent 有时不在预期的 Slack thread 中回复。

**影响**：用户在 Slack 中看不到 Agent 的执行过程。

**应对**：
- 使用 Round0 审计握手验证 session 链路（见 A2A_PROTOCOL.md）
- 如看不到 Round0 回传，说明 session 可能绑定到 webchat 而非 Slack
- 补发兜底消息到 thread

---

## P1: 长任务上下文溢出

**现象**：超过 20 轮对话或大量工具输出后，Agent 的上下文窗口接近极限，回复质量下降。

**影响**：Agent 可能遗忘早期指令或数据。

**应对**：
- 严格执行 Checkpoint 机制（>20 轮自动切割）
- Closeout 控制在 10-15 行
- 大量数据任务使用 spawn 子任务并行处理
- `compaction.mode: "safeguard"` 配置已启用自动压缩

---

## P1: sessions_send 超时

**现象**：`sessions_send` 返回 timeout 错误。

**影响**：派单方不确定消息是否送达。

**实际情况**：timeout ≠ 未送达。消息可能已送达并被处理。

**应对**：
- 在 Slack thread 补发兜底消息
- 检查目标 Agent 频道是否有响应
- 不要因 timeout 重复派单

---

## P2: 跨 Session 知识检索

**现象**：无法语义搜索跨多个 session 的历史知识。

**影响**：需要手动查找历史决策和分析。

**应对**：
- 依赖 Closeout 总结 + KO 知识库索引
- 重要决策都有 `decisions/YYYY-MM-DD-SYMBOL.md` 记录
- 未来可接入向量搜索增强

---

## P2: 飞书无 Thread 隔离

**现象**：飞书群组内对话扁平，无法像 Slack 用 thread 隔离任务。

**影响**：并行任务上下文可能混杂。

**应对**：
- Agent 回复带任务 ID 前缀：`[TID:20260409] ...`
- 复杂任务创建临时群组
- 简单查询（Q 类）影响较小

---

## P2: Discord A2A v2 不可用

**现象**：Discord 平台不支持 A2A v2 讨论模式（多 Agent 同 thread 协作）。

**影响**：跨 Agent 协作只能用 `sessions_spawn` 委派模式。

**应对**：
- 使用 `sessions_spawn` 替代
- 接受单向委派模式（CIO 派单 → Research 回传）
- 需要多轮协作时，转到 Slack 处理

---

## P2: 脚本阈值与 SOUL.md 不一致

**现象**：手动修改 Python 脚本中的止损止盈阈值，但忘记同步 SOUL.md（或反之）。

**影响**：CIO Agent 的判断与自动脚本的执行出现矛盾。

**应对**：
- Ops Agent 周度审计会检查一致性
- 修改阈值时同时修改两处（脚本 + SOUL.md）
- 长期方案：从 SOUL.md 或 watchlist.yaml 统一读取阈值
