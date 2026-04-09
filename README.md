# 🤖 US Stock Investment Team

**一套可直接部署的美股 AI 多智能体投研系统**，基于 [OpenClaw](https://openclaw.ai) 构建，4 个 Agent 协同工作，从调研、决策到执行全自动化。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw](https://img.shields.io/badge/Powered%20by-OpenClaw-blue)](https://openclaw.ai)

---

## 🏗️ 系统架构

```
用户
  │
  ▼
┌─────────────────────────────────────────────────────┐
│                    CIO Agent                        │
│  交易执行 · 持仓监控 · 止损止盈 · 决策验证            │
└──────────┬──────────────────────┬────────────────────┘
           │ A2A 派单              │ A2A 派单
           ▼                      ▼
┌──────────────────┐    ┌─────────────────────┐
│  Research Agent  │    │      KO Agent        │
│ 调研·数据·新闻    │    │  策略沉淀·决策日志   │
└──────────────────┘    └─────────────────────┘
           │
           │ 专业数据查询
           ▼
┌──────────────────────────────────────────────────────┐
│                   Advisor Agent                      │
│    Stock AI · FX Pricing · Fund Advisory            │
└──────────────────────────────────────────────────────┘
```

### Agent 分工

| Agent | 职责 | 工具 |
|-------|------|------|
| **CIO** | 交易执行、持仓监控、止损止盈、决策验证 | Alpaca API, yfinance |
| **Research** | 新闻搜索、行业调研、财务数据、标的筛选 | yfinance, akshare, RSS |
| **KO** | 投资策略整理、原则维护、决策日志 | 文档写作 |
| **Advisor** | 专业投顾数据（Stock/FX/Fund） | Finance Advisory API |

---

## ✨ 核心特性

- ✅ **全自动多 Agent 协作**：CIO → Research → KO 三角协作，A2A 可见派单
- ✅ **自动止损止盈**：盘中每 30min 检查，分级止盈（8%/15%/25%）分级止损（12%/18%）
- ✅ **盘前事件扫描**：美股开盘前自动扫描隔夜重大事件
- ✅ **多源交叉验证**：至少 2 个独立信息源验证，防止单源误判
- ✅ **策略知识积累**：KO 自动维护投资原则库和决策日志
- ✅ **完全可定制**：修改 `SOUL.md` 配置每个 Agent 的角色和策略

---

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装 OpenClaw
npm install -g openclaw

# 安装 Python 依赖
pip install yfinance akshare alpaca-trade-api pandas numpy

# 可选：部署本地搜索引擎（推荐）
docker run -d --name searxng -p 8888:8888 searxng/searxng
```

### 2. 克隆 & 一键部署

```bash
git clone https://github.com/IanLiYi1996/us-stock-investment-team.git
cd us-stock-investment-team

# 一键部署（创建目录、复制配置、设置 Alpaca 密钥）
chmod +x setup.sh && ./setup.sh
```

### 3. 配置 OpenClaw（关键步骤）

```bash
# 复制 OpenClaw 主配置模板
cp openclaw/openclaw.example.json ~/.openclaw/openclaw.json

# 编辑，填入：Slack Bot Token、App Token、各频道 ID
nano ~/.openclaw/openclaw.json
```

详细 Slack 配置步骤见 **[docs/openclaw-setup.md](docs/openclaw-setup.md)**

### 4. 配置定时任务

```bash
# 复制 cron 模板
cp openclaw/cron/cron.example.json ~/.openclaw/cron/cron.json

# 编辑，替换频道 ID
nano ~/.openclaw/cron/cron.json
```

### 5. 启动

```bash
# 启动 OpenClaw Gateway
openclaw gateway start

# 验证 Agent 状态
openclaw agents list

# 在 Slack #invest-us-market 频道发消息测试
# → "@CIO 分析一下 AAPL 现在值得买吗"
```

---

## 📁 项目结构

```
us-stock-investment-team/
├── openclaw/                  # ⭐ OpenClaw 核心配置（最先配置这里）
│   ├── openclaw.example.json  # Agent注册 + Slack绑定 + 频道路由
│   └── cron/
│       └── cron.example.json  # 定时任务（盘前扫描/收盘总结/新闻简报）
├── agents/                    # 各 Agent 配置模板
│   ├── cio/                   # CIO - 交易执行
│   │   ├── SOUL.md            # 投资策略、止损规则、自主权边界
│   │   ├── AGENTS.md          # 工作流程
│   │   ├── TOOLS.md           # Alpaca/yfinance 使用参考
│   │   └── IDENTITY.md        # Agent 身份
│   ├── research/              # Research - 调研分析
│   ├── ko/                    # KO - 知识沉淀
│   └── advisor/               # Advisor - 投顾服务（可选）
├── shared/                    # 全局共享规则
│   ├── SYSTEM_RULES.md        # 系统准则（自主权阶梯、任务分类）
│   ├── A2A_PROTOCOL.md        # Agent 间协作协议
│   └── TASK_PROTOCOL.md       # 任务分类与台账
├── scripts/                   # 自动化脚本
│   ├── stock_analysis.py      # 基本面+技术面分析
│   ├── pre_market_scan.py     # 盘前事件扫描
│   ├── overnight_monitor.py   # 盘后持仓监控
│   ├── trading_monitor.py     # 盘中止损止盈
│   └── run_monitor.sh         # 监控守护脚本
├── config/                    # 配置模板
│   ├── watchlist.example.yaml # 观察清单（持仓标的+止损阈值）
│   └── alpaca.example.env     # API 密钥模板
├── principles/                # 投资原则模板
│   └── INVESTMENT_FRAMEWORK.md
├── docs/                      # 详细文档
│   ├── openclaw-setup.md      # ⭐ OpenClaw 配置指南（Slack/Agent/Cron）
│   ├── architecture.md        # 系统架构说明
│   ├── agents.md              # Agent 配置指南
│   ├── setup.md               # 完整安装指南
│   └── customization.md       # 策略定制指南
└── setup.sh                   # 一键部署脚本
```

---

## 📊 止损止盈规则（默认配置）

| 类型 | 触发条件 | 操作 |
|------|---------|------|
| 止盈第一级 | 盈利 ≥ 8% | 卖出 30% |
| 止盈第二级 | 盈利 ≥ 15% | 再卖出 30% |
| 止盈第三级 | 盈利 ≥ 25% | 仅保留 10% |
| 止损第一级 | 亏损 ≥ 12% | 减仓 50% |
| 止损第二级 | 亏损 ≥ 18% | 全部清仓 |

> 可在 `agents/cio/SOUL.md` 中修改这些参数。

---

## 🔧 定制化指南

### 修改投资策略

编辑 `agents/cio/SOUL.md` 中的策略部分：
- 持仓标的（`US_STOCKS`）
- 止损止盈阈值
- 仓位管理规则

### 修改调研范围

编辑 `agents/research/SOUL.md`：
- 重点关注行业
- 数据源优先级
- 报告格式

### 添加新数据源

参考 `shared/TOOLS_REFERENCE.md` 中的 RSS/API 列表，按格式添加新数据源。

---

## 📚 文档

- [⭐ OpenClaw 配置指南](docs/openclaw-setup.md) — **最重要，先看这个**
- [详细安装指南](docs/setup.md)
- [Agent 配置指南](docs/agents.md)
- [系统架构说明](docs/architecture.md)
- [策略定制指南](docs/customization.md)

---

## ⚠️ 免责声明

本项目仅供学习和研究使用。默认使用 **Alpaca Paper Trading（模拟盘）**，不涉及真实资金。

**在连接真实账户前，请确保：**
1. 充分理解系统运作原理
2. 在模拟盘验证策略有效性
3. 根据自身风险承受能力调整止损阈值

本项目作者不承担任何投资损失责任。

---

## 🤝 贡献

欢迎 PR 和 Issue！特别欢迎：
- 新的数据源集成
- 更多策略模板
- 文档改进

---

## 📄 License

MIT © [IanLiYi1996](https://github.com/IanLiYi1996)
