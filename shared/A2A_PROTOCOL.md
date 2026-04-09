# A2A 协作协议（Slack 多 Agent）

> 目标：让 Agent 之间的协作 **自动发生在正确的 Slack 频道/线程里**，做到：
> - 可见（用户 能在频道里看到）
> - 可追踪（每个任务一个 thread/session）
> - 不串上下文（thread 级隔离 + 任务包完整）

---

## 0. 术语

- **A2A（本文）**：Agent-to-Agent 协作流程（不等同于 OpenClaw 的某一个单独工具名）。
- **Task Thread**：在目标 Agent 的 Slack 频道里创建的任务线程；该线程即该任务的独立 Session。

---

## 1) 权限矩阵（必须遵守）

- CoS → 只能给 CTO 派单/对齐方向（默认不直达 Builder）
- CTO → 可以派单给 Builder / Research / KO / Ops
- Builder → 只接单执行；需要澄清时回到 CTO thread 提问
- CIO → 尽量独立；仅必要时与 CoS/KO 同步
- KO/Ops → 作为审计/沉淀，通常不主动派单

（注：技术上 Slack bot 可以给任意频道发消息，但这是组织纪律，不遵守视为 bug。）

---

## 2) A2A 触发方式（核心）

当 A 想让 B 开工时（**不允许人工复制粘贴**）：

> ⚠️ 重要现实：Slack 中所有 Agent 共用同一个 bot 身份。
> **bot 自己发到别的频道的消息，默认不会触发对方 Agent 自动运行**（OpenClaw 默认忽略 bot-authored inbound，避免自循环）。
> 因此：跨 Agent 的"真正触发"必须通过 **sessions_send（agent-to-agent）** 完成；Slack 发消息仅作为"可见性锚点"。

### Step 1 - 在目标频道创建可见的 root message（锚点）
A 在 B 的 Slack 频道创建一个任务根消息（root message），第一行固定前缀：

```
A2A <FROM>→<TO> | <TITLE> | TID:<YYYYMMDD-HHMM>-<short>
```

正文必须是完整任务包（建议使用 `~/.openclaw/shared/SUBAGENT_PACKET_TEMPLATE.md`）：
- Objective（目标）
- DoD（完成标准）
- Inputs（已有信息/链接/文件）
- Constraints（约束/边界）
- Output format（输出格式）
- CC（需要同步到哪个频道/人）

> 前置条件：OpenClaw bot 必须被邀请进目标频道，否则会报 `not_in_channel`。

### Step 2 - 用 sessions_send 触发 B 在该 thread/session 中运行
A 读取 root message 的 Slack message id（ts），拼出 thread sessionKey：

- 频道 session：`agent:<B>:slack:channel:<channelId>`
- 线程 session：`agent:<B>:slack:channel:<channelId>:thread:<root_ts>`

然后 A 用 `sessions_send(sessionKey=..., message=<完整任务包或第一步的引用>)` 触发 B。

> ⚠️ **timeout 容错**：`sessions_send` 返回 timeout **≠ 没送达**。消息可能已送达并被处理。
> 规避：在 Slack thread 里补发一条兜底消息（"已通过 A2A 发送，如未收到可在此查看全文"）。

> ⚠️ **SessionKey 注意**：不要手打 sessionKey。优先从 `sessions_list` 复制 `deliveryContext=slack` 的 key。
> 注意 channel ID 大小写一致性——大小写不一致可能导致 session 被拆分，路由到 webchat 而非 Slack。

### Step 3 — 执行与汇报
- B 的执行与产出都留在该 thread。
- 需要上游（如 CTO）掌控节奏时，上游应在自己的协调 thread 里同步 checkpoint/closeout（见第 3 节）。

---

## 2.5) 多轮 WAIT 纪律（实战验证）

当 A2A 任务需要多轮迭代时（大部分非 Q 类任务都是）：

- **每轮只聚焦 1-2 个改动点**，完成后**必须 WAIT**。
- **禁止一次性做完所有步骤**--等上游下一轮指令后再继续。
- 每轮输出格式固定：
  ```
  [<角色>] Round N/M
  Done: <做了什么>
  Run: <执行了什么命令>
  Output: <关键输出，允许截断>
  WAIT: 等待上游指令
  ```
- 最终轮贴 closeout 到 thread，A2A reply 中回复 `REPLY_SKIP` 表示完成。

### Round0 审计握手（推荐）

在正式 Round1 前，先做一个**极小的真实动作**验证审计链路：
- 要求目标 Agent 执行一个无副作用命令（如 `pwd`）并把结果贴到 Slack thread。
- **看不到 Round0 回传就停止**--说明目标 Agent 的 session 可能没绑定 Slack（deliveryContext 落到 webchat），继续执行会导致"在跑但 Slack 不可审计"。

---

## 3) 可见性（用户 必须能看到）

- 任务根消息必须在目标频道可见（root message 作为锚点）。
- 关键 checkpoint（开始/阻塞/完成）至少更新 1 次。
- **上游负责到底**：谁派单（例如 CTO 派给 Builder），谁负责在自己的协调 thread 里持续跟进：
  - Builder thread 的输出由 CTO 通过 sessions_send 的 tool result 捕获
  - CTO 必须在 #cto 的对应协调 thread 里同步 checkpoint（避免 用户 去多个频道"捞信息"）
- **双通道留痕**：
  - A2A reply（给上游的结构化回复）
  - Slack thread message（给用户可见的审计日志，格式 `[角色] 内容...`）
  - **两者都要做**--A2A reply 只有上游能看到，thread message 用户才能看到。
- 完成后必须 closeout（DoD 硬规则，缺一不可）：
  1. 在目标 Agent thread 贴 closeout（产物路径 + 验证命令）
  2. **上游本机复核**（CLI-first）：至少执行关键命令 + 贴 exit code
  3. **回发起方频道汇报**：同步最终结果 + 如何验证 + 风险遗留。**不做视为任务未完成**
  4. 通知 KO 沉淀（默认：同步到 #know + 触发 KO ingest）

---

## 4) 频道映射（约定）

- #hq → CoS
- #cto → CTO
- #build → Builder
- #invest → CIO
- #know → KO
- #ops → Ops
- #research → Research
- #main（可选：你的主入口频道） → Main Agent（可选）（不属于本系统，但可作为 用户 的总入口）

---

## 5) 命名与并行

- **一个任务 = 一个 thread = 一个 session**。
- 同一个频道可以并行多个任务 thread；不要在频道主线里混聊多个任务。

---

## 6) 失败回退

如果 Slack thread 行为异常：
- 退回到"单频道单任务"：临时在频道主线完成该任务
- 或让 CTO/CoS 在 thread 里发 /new 重置（开始新 session id）
