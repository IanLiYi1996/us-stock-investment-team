# 系统演进记录（Journey）

> 记录本项目的设计决策和演进过程，帮助理解"为什么是现在这个样子"。

---

## Phase 1：基础框架（初始版本）

### 设计目标
构建一个能自动执行美股模拟盘交易的 AI 系统。

### 关键决策
- **选择 OpenClaw** 作为 Agent 框架（vs CrewAI/AutoGen）：OpenClaw 原生支持 Slack 集成，Agent 间协作对用户可见
- **4 Agent 架构**：CIO（执行）、Research（调研）、KO（知识）、Advisor（数据）
- **Alpaca Paper Trading**：免费模拟盘，API 友好，适合验证策略

### 产出
- 4 个 Agent 的 SOUL.md / AGENTS.md / IDENTITY.md
- Python 自动化脚本（止损止盈、盘前扫描）
- 基础 A2A 协作协议

---

## Phase 2：协作治理（借鉴 OpenCrew）

### 发现的问题
- 协议引用的文件（MEMORY.md、TASKS.md）实际不存在
- A2A 协议中残留 OpenCrew 的 CoS/CTO/Builder 角色引用
- 缺少系统审计机制，Agent 自我修改无人监督
- 知识沉淀缺乏结构化模板

### 从 OpenCrew 吸收的优秀实践
1. **每 Agent 配置文件体系**：USER.md（用户画像）、MEMORY.md（长期记忆）、TASKS.md（任务台账）、HEARTBEAT.md（自检清单）
2. **Ops Agent**：系统审计官，防止配置漂移
3. **结构化模板**：Closeout、Checkpoint、Self-Update、Subagent Packet
4. **Signal Score（0-3）**：量化知识价值，驱动 KO 精准提炼
5. **CoS 协调纪律融入 CIO**：决策架构、消息简洁、每日简报
6. **防膨胀规则**：消息长度限制、双通道汇报、checkpoint 硬触发
7. **软硬约束区分**：明确哪些规则靠 LLM 遵守，哪些靠配置强制

### 刻意不采纳的内容
- **CoS 独立 Agent**：投资场景时效性要求高，多一层协调 = 多一层延迟
- **CTO/Builder Agent**：投资系统不是开发项目
- **A2A v2 独立 App 模式**：单 Bot 足够，复杂度不值得
- **v2-lite 精简架构**：5 Agent 已足够精简

---

## Phase 3：多平台与文档完善

### 扩展内容
- **Discord 接入**：配置模板 + 详细设置指南
- **飞书接入**：配置模板 + 详细设置指南（含 thread 隔离限制说明）
- **概念文档**：系统设计哲学（频道即岗位、自主权阶梯、QAPS、知识三层架构）
- **Agent 入职指南**：6 步学习路径
- **已知问题**：P0-P2 分级，含应对策略
- **FAQ**：常见问题汇总
- **TOOLS.md 补齐**：KO、Ops、Advisor 全部有工具文档
- **Knowledge 模板**：principles / patterns / scars 独立文件

---

## 设计原则总结

经过多轮迭代，形成以下核心设计原则：

1. **频道即岗位**：组织结构映射到通信平台，一目了然
2. **可见即可审计**：所有 Agent 协作在频道中可见，不搞暗箱操作
3. **结构化压缩**：海量对话 → Closeout → 原则，25 倍压缩
4. **硬约束优先**：关键业务规则用配置强制，不单纯依赖 LLM 遵守
5. **可逆设计**：所有变更可回滚，所有修改有记录
6. **专业化而非通用化**：投资领域深耕，不追求通用框架
7. **渐进演化**：从 OpenCrew 吸收成熟模式，但根据投资场景适配

---

## 未来方向

- [ ] 向量搜索：跨 session 语义检索历史决策
- [ ] 真实账户接入：从模拟盘过渡到实盘（需要更严格的 L3 审批流程）
- [ ] 更多数据源：SEC Filing 自动解析、卫星数据、社交情绪
- [ ] 回测框架：用历史数据验证策略有效性
- [ ] Dashboard：可视化持仓、盈亏、知识库状态
