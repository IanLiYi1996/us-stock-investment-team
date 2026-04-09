# Agent 配置指南

## CIO Agent（首席投资官）

### 核心配置文件

**`agents/cio/SOUL.md`** — 最重要的配置文件

需要定制的关键部分：

```markdown
# 修改持仓标的
US_STOCKS = ['NVDA', 'AMZN', 'TSM', 'MU', 'AAPL']
# ↑ 替换为你自己想跟踪的美股标的

# 修改止损止盈阈值
| 止盈第一级 | 盈利 ≥ 8%  | 卖出 30% |
| 止盈第二级 | 盈利 ≥ 15% | 再卖出 30% |
# ↑ 根据你的风险承受能力调整

# 修改频道 ID（运行 setup.sh 后会提示）
RESEARCH_CHANNEL_ID = "C0AJ5AJQP8S"  # ← 填你的
KO_CHANNEL_ID       = "C0AJJ83K0P3"  # ← 填你的
CIO_CHANNEL_ID      = "C0AJ5AGUW3C"  # ← 填你的
```

### 自主权配置

在 `SOUL.md` 中调整 CIO 的自主执行权限：

```markdown
## 允许自主执行（无需用户确认）
- 建仓 / 补仓 / 减仓 / 清仓 / 止损 / 止盈   ← 可以限制这里

## 必须用户确认
- 真实账户 / 真实资金划转
- 单笔超过总资产 30% 的重大仓位变动         ← 可以降低这个阈值
```

---

## Research Agent（调研分析师）

### 配置调研重点

编辑 `agents/research/SOUL.md`：

```markdown
## 调研重点行业（可定制）
- AI / 人工智能（默认）
- 半导体
- 云计算
- 生物医药         ← 按需增减
- 新能源
```

### 配置数据源优先级

编辑 `agents/research/TOOLS.md` 中的 `RSS_FEEDS`：
- 删除不需要的源，添加你关注的媒体
- 中国用户可优先使用 CN_FEEDS（财联社、36kr 等）

---

## KO Agent（知识官）

KO 主要通过 CIO 的 A2A 派单驱动，通常无需大量配置。

建议定制：
- `agents/ko/SOUL.md` → 调整决策日志格式和 Signal Score 处理规则
- `agents/ko/USER.md` → 设置复盘频率和知识格式偏好
- `principles/INVESTMENT_FRAMEWORK.md` → 填写你自己的投资哲学

---

## Ops Agent（系统审计官）

Ops 负责系统治理，防止配置漂移和质量退化。

### 核心配置

**`agents/ops/SOUL.md`** — 审计规则和硬性拦截条件

关键定制：
- 硬性拦截条件（哪些变更必须 Ops 审核）
- 审计节奏（周/月/季的频率）
- 五维评估标准的权重

### 审计节奏

| 周期 | 内容 |
|------|------|
| 每周 | S 类 closeout + Self-Update 审计 + 阈值一致性检查 |
| 每月 | MEMORY 去重 + KO 质量审核 + SYSTEM_RULES 检查 |
| 每季 | 全面系统健康检查 + 知识库价值回顾 |

详见 `shared/OPS_REVIEW_PROTOCOL.md`

---

## 每 Agent 通用配置文件

所有 Agent 除 SOUL.md/AGENTS.md/IDENTITY.md 外，还可配置：

| 文件 | 用途 | 说明 |
|------|------|------|
| `USER.md` | 用户画像 | 风险偏好、沟通习惯、特殊约束 |
| `MEMORY.md` | 长期记忆 | 验证过的原则、踩坑记录 |
| `TASKS.md` | 任务台账 | 活跃任务追踪 |
| `HEARTBEAT.md` | 自检清单 | 仅 CIO 和 KO |

---

## Advisor Agent（可选）

如果你有专业投顾 API 访问权限，编辑 `agents/advisor/SOUL.md`：

```markdown
COGNITO_AUTH_DOMAIN=your_auth_domain
COGNITO_USER_POOL=your_pool_id
COGNITO_CLIENT_ID=your_client_id
```

**如果没有投顾 API**：可以完全跳过此 Agent，Research Agent + yfinance 已足够满足大多数需求。

---

## 监控脚本配置

> **重要**：修改脚本中的止损止盈阈值时，必须同步修改 `agents/cio/SOUL.md` 中的对应规则，保持一致。Ops Agent 会周期性检查脚本与 SOUL.md 的阈值一致性。

### `scripts/pre_market_scan.py`

```python
# 修改监控的标的列表（第 16-17 行）
US_STOCKS = ['NVDA', 'AMZN', 'TSM', 'MU', 'UNH']  # ← 改为你的

# 修改 Tavily API Key（第 21 行）
"api_key": "YOUR_TAVILY_API_KEY",  # ← 填入你的 key
```

### `scripts/overnight_monitor.py`

```python
# 止盈止损阈值（第 42-53 行）
# TP: >=8% sell 30%, >=15% sell another 30%, >=25% leave only 10%
# SL: >=12% cut 50%, >=18% liquidate
```

### `scripts/trading_monitor.py`

类似配置，同步修改阈值以保持一致性。

---

## 定时任务配置

```bash
# 查看当前 cron 任务
crontab -l

# 编辑
crontab -e

# 推荐配置（美东夏令时 UTC-4）
# 盘前扫描（美股开盘前 30min）
0 13 * * 1-5 cd /path/to/project && python3 scripts/pre_market_scan.py >> logs/pre_market.log 2>&1

# 盘中监控（每 30min，美股交易时段）
*/30 13-20 * * 1-5 python3 /path/to/scripts/trading_monitor.py >> logs/trading.log 2>&1

# 盘后监控（收盘后 1h）
0 22 * * 1-5 python3 /path/to/scripts/overnight_monitor.py >> logs/overnight.log 2>&1
```
