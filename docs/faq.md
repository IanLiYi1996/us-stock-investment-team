# 常见问题（FAQ）

---

## 系统设计

### Q: 为什么用多 Agent 而不是一个全能 Agent？

**A:** 单个 Agent 的上下文窗口有限，当同时处理交易执行、市场调研、知识沉淀时，容易产生上下文膨胀和角色混乱。多 Agent 架构实现：
- **上下文隔离**：每个 Agent 只关注自己的领域，不被无关信息干扰
- **专业化**：CIO 专注交易逻辑，Research 专注数据质量，KO 专注知识提炼
- **可审计**：所有协作在 Slack 频道可见，出问题时可追溯

### Q: 为什么没有 CoS（Chief of Staff）Agent？

**A:** OpenCrew 原版有 CoS 作为独立协调层。本项目刻意不加，原因：
- 投资场景对**时效性**要求高，多一层协调 = 多一层延迟
- CIO 已吸收 CoS 的协调纪律（决策架构、消息简洁、每日简报）
- 4-5 个 Agent 的规模不需要独立协调者

### Q: 为什么没有 Builder/CTO Agent？

**A:** 这是投资系统，不是软件开发项目。Builder/CTO 是 OpenCrew 为代码开发场景设计的角色，投资场景不需要。

### Q: 5 个 Agent 够用吗？

**A:** 对个人投资者完全够用：
- **CIO**：交易执行 + 团队协调
- **Research**：数据调研
- **KO**：知识沉淀
- **Ops**：系统治理（防止 AI 系统漂移）
- **Advisor**：专业数据查询（可选）

如果需要更多能力，可以通过给现有 Agent 添加工具（TOOLS.md）来扩展，而非新增 Agent。

---

## 部署与成本

### Q: 运行这套系统需要多少成本？

**A:** 主要成本是 LLM API 调用费用：
- **模型选择**：Claude Sonnet（推荐，性价比最优）或 GPT-4o
- **日常运行**：4 个 cron 任务 + 2 个 heartbeat + 用户交互，预估每日 $1-5
- **高频交易日**：如果多次调研+交易，可能 $5-15/天
- **基础设施**：Slack 免费版够用，Alpaca Paper Trading 免费

### Q: 需要什么硬件？

**A:** 
- 最低配置：任何能运行 Node.js 的机器（可以是笔记本、VPS、树莓派）
- 推荐配置：一台常开的 VPS/云服务器（保证 cron 任务和监控脚本持续运行）
- 不需要 GPU

### Q: 支持哪些 LLM？

**A:** OpenClaw 支持：
- Anthropic Claude（推荐）
- Amazon Bedrock
- OpenAI GPT
- 详见 [docs.openclaw.ai/models](https://docs.openclaw.ai/models)

---

## 平台选择

### Q: Slack、Discord、飞书选哪个？

| 考虑因素 | Slack | Discord | 飞书 |
|---------|-------|---------|------|
| A2A 完整性 | ⭐⭐⭐ 最完整 | ⭐⭐ 委派模式 | ⭐⭐ 委派模式 |
| Thread 隔离 | ✅ | ✅ | ❌ |
| 免费版限制 | 90天消息历史 | 无限制 | 视企业版本 |
| 部署难度 | 中等 | 较低 | 中等 |
| 适合场景 | 专业团队 | 个人/小团队 | 企业用户 |

**推荐**：首选 Slack（功能最完整），个人用户可选 Discord（免费无限制）。

### Q: 能同时用多个平台吗？

**A:** 可以。在 `openclaw.json` 中同时配置多个 channel，同一 Agent 可绑定不同平台的频道。但建议选定一个主平台，避免消息分散。

---

## 交易与策略

### Q: 会自动用真钱交易吗？

**A:** **不会**。默认使用 Alpaca Paper Trading（模拟盘），所有交易都是虚拟的。真实账户交易属于 L3 级别，必须用户明确授权。

### Q: 止损止盈阈值怎么调？

**A:** 两处都要改（保持一致）：
1. `agents/cio/SOUL.md` — Agent 的判断依据
2. `scripts/trading_monitor.py` 和 `scripts/overnight_monitor.py` — 自动脚本的执行逻辑

Ops Agent 会周度检查两者一致性。

### Q: 能做空吗？能做期权吗？

**A:** 默认配置不做空、不做期权。如需启用：
- 在 `agents/cio/SOUL.md` 中修改自主权边界
- 在 `agents/cio/USER.md` 中更新用户约束
- Alpaca Paper Trading 支持做空和部分期权

### Q: 能投 A 股/港股吗？

**A:** 当前设计专注美股。CIO SOUL.md 明确写了"只做美股，不投资港股"。如需扩展：
- 修改 CIO SOUL.md 的投资范围
- Research TOOLS.md 已包含 akshare（A 股数据源）
- 交易执行需要接入对应的券商 API

---

## 运维与安全

### Q: Agent 会不会"失控"修改策略？

**A:** 有多层防护：
1. **自主权阶梯**：L3 级别操作（真实交易、删除数据）必须用户确认
2. **Self-Update 审计**：所有自我修改必须记录动机和回滚方案
3. **Ops 硬性拦截**：修改止损阈值、L3 权限等需 Ops 审核
4. **周度审计**：Ops 每周检查配置一致性和策略漂移

### Q: 数据安全怎么保障？

**A:**
- API 密钥存储在 `~/.alpaca/credentials`，权限 600
- Slack/Discord Token 不应硬编码在代码中
- 建议使用环境变量管理敏感信息
- 模拟盘交易不涉及真实资金风险

### Q: 系统挂了怎么办？

**A:**
- 检查 `openclaw gateway status`
- 查看日志 `openclaw logs --follow`
- 重启 `openclaw gateway restart`
- 监控脚本：`bash scripts/run_monitor.sh`
- 详见 [docs/known-issues.md](docs/known-issues.md)
