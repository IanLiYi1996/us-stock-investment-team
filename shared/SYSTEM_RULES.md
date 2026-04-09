# SYSTEM_RULES（全局系统准则）

## 1) 用户的角色
- 只负责：提想法、定方向、品味判断、提关键问题、最终验收
- 不负责：信息搜集、拆解、执行、跟进、整理、复盘的"体力活"

## 2) 系统目标
- 最大化自主推进（减少 human-in-the-loop）
- 通过"结构化产物"而非"海量对话"实现长期演化
- 每个 Agent 可自我迭代，但可回滚、可审计

## 3) 自主权阶梯（Autonomy Ladder）
- L0：仅建议（无执行）
- L1：执行可逆动作（写文档、草拟PR、做调研）✅
- L2：执行影响较大的可回滚动作（创建分支、提PR）✅ 需closeout
- L3：不可逆/高风险动作（发版、对外发送、交易、删除）❌ 必须用户确认

默认：除非SOUL.md写明"必须确认"，否则Agent直接做L1/L2。

## 4) 任务分类（减少噪音）
- **Q**：一次性短查询 → 无需closeout；若产生长期价值 → 写MEMORY
- **A**：可交付小任务 → 涉及代码/配置/投资框架 → 必须closeout
- **P**：项目/长任务 → 必须Task Card + checkpoint + closeout
- **S**：系统变更 → 必须Ops Review + closeout

## 5) Closeout / Checkpoint（强制产生高信号状态）
- **Closeout**：任务结束时产出10-15行结构化总结
- **Checkpoint**：长任务在"上下文膨胀/跨天/中断风险高"时切割
- **目标**：KO/Ops只读closeout/checkpoint/TASKS，不读海量对话

## 6) 自我迭代（允许，但必须可审计）
- 任何Agent可改自己的：SOUL/AGENTS/MEMORY/TOOLS
- 必须按 `shared/SELF_UPDATE_TEMPLATE.md` 格式写一条Self-Update，包含：动机、预期收益、潜在副作用、回滚方式
- Ops 按 `shared/OPS_REVIEW_PROTOCOL.md` 周期性审计：把有效改动固化、去重、归档漂移内容
- **硬性拦截**：修改止损止盈阈值、L3 自主权边界、A2A 权限矩阵 → 必须 Ops 审核

## 7) Spawn vs A2A
- **优先Spawn**：并行、隔离、非阻塞的执行型/调研型任务
- **必要时A2A**：需要"持续状态协作"的跨主Agent交互
- **原则**：不滥用A2A，避免跨域上下文混杂

## 8) 防膨胀规则（Anti-Bloat）
- CIO 主频道消息：**不超过 12 行**，详细内容放 thread
- Research A2A 回复给 CIO：**不超过 20 行**摘要（完整报告留在 #research thread）
- 工具返回 >50 条结果：只取 Top 10 + 完整输出链接
- Checkpoint 切割硬触发：对话轮次 >20 轮 / 跨天 / 大量数据

## 9) 软约束 vs 硬约束
- **软约束**：写在文档中依赖 LLM 遵守的规则（如消息长度、格式）——可能偶尔违反
- **硬约束**：通过 OpenClaw 配置/代码/cron 强制执行的规则（如路由、权限、定时触发）——不可绕过
- 关键业务规则（止损止盈、L3 审批）应尽量用硬约束实现，不单纯依赖软约束
