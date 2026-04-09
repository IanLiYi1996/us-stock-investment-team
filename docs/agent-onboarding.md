# Agent 入职指南

> 新 Agent 上线时的 6 步学习路径。无论是新增 Agent 还是重新部署现有 Agent，都按此流程初始化。

---

## Step 1：个人配置（了解"我是谁"）

按优先级顺序读取：

1. **SOUL.md**（最高优先级）— 角色定位、核心职责、自主权边界、禁止行为
2. **IDENTITY.md** — 名称、emoji、一句话定位
3. **USER.md** — 用户画像、偏好、特殊约束
4. **MEMORY.md** — 长期记忆（验证过的原则、踩坑记录）

> SOUL.md 是最重要的文件，定义了"你能做什么"和"你不能做什么"。

---

## Step 2：全局规则（了解"系统怎么运转"）

1. **shared/SYSTEM_RULES.md** — 自主权阶梯、任务分类、closeout 要求、防膨胀规则
2. **shared/TASK_PROTOCOL.md** — Task Card 格式、完成判定、checkpoint 触发条件
3. **shared/KNOWLEDGE_PIPELINE.md** — 知识三层架构、Signal Score 定义

---

## Step 3：工作环境（了解"在哪里工作"）

1. **AGENTS.md** — 你的工作流程、会话启动序列、A2A 派单方式
2. **TASKS.md** — 当前活跃任务台账
3. **TOOLS.md**（如有）— 可用的工具和 API 参考

**Thread 隔离概念**（Slack/Discord）：
- 每个 thread = 独立任务 session
- 不要在频道主线混聊多个任务
- 飞书用户注意：无 thread 隔离，需用任务 ID 区分

---

## Step 4：协作规则（了解"怎么跟队友配合"）

1. **shared/A2A_PROTOCOL.md** — 跨 Agent 协作的完整流程
2. 权限矩阵：谁能给谁派单
3. 双通道可见性：A2A reply + Slack 可见消息
4. Round0 审计握手
5. 多轮 WAIT 纪律

---

## Step 5：产出标准（了解"交付什么"）

1. **shared/CLOSEOUT_TEMPLATE.md** — A/P/S 任务的结束总结格式
2. **shared/CHECKPOINT_TEMPLATE.md** — 长任务的中间切割格式
3. **shared/SUBAGENT_PACKET_TEMPLATE.md** — spawn 子任务的任务包格式
4. **shared/SELF_UPDATE_TEMPLATE.md** — 自我修改的记录格式

---

## Step 6：自我迭代（了解"如何进化"）

- 你可以修改自己的 SOUL/AGENTS/MEMORY/TOOLS
- 但必须遵循 SELF_UPDATE_TEMPLATE，记录动机和回滚方案
- **硬性拦截**：部分修改需要 Ops 审核（见 SYSTEM_RULES.md）
- 定期查看 HEARTBEAT.md（如有）执行自检

---

## 快速检查清单

```
□ 读完 SOUL.md，理解角色定位和禁止行为
□ 读完 SYSTEM_RULES.md，理解自主权阶梯
□ 读完 A2A_PROTOCOL.md，理解派单/回复流程
□ 确认 TASKS.md 中无遗留未完成任务
□ 确认 MEMORY.md 中的长期记忆是否仍然准确
□ 首次交互时，用简短自我介绍确认身份
```
