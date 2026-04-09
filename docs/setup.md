# 详细安装指南

## 前置要求

| 要求 | 版本 | 必须/可选 |
|------|------|---------|
| Node.js | ≥ 18 | 必须（OpenClaw 依赖）|
| Python | ≥ 3.9 | 必须 |
| Docker | 任意 | 可选（SearXNG 本地搜索）|
| Slack workspace | — | 必须（Agent 通信平台）|
| Alpaca 账户 | — | 必须（Paper Trading）|

---

## Step 1：安装 OpenClaw

```bash
# 安装 OpenClaw CLI
npm install -g openclaw

# 验证安装
openclaw --version

# 登录（需要 OpenClaw 账户）
openclaw login
```

> 注册 OpenClaw：https://openclaw.ai

---

## Step 2：安装 Python 依赖

```bash
# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install yfinance akshare pandas numpy alpaca-trade-api requests pyyaml
```

---

## Step 3：配置 Alpaca Paper Trading

1. 注册 Alpaca 账户：https://app.alpaca.markets/signup
2. 进入 Paper Trading 账户，获取 API Key
3. 配置密钥：

```bash
mkdir -p ~/.alpaca
cat > ~/.alpaca/credentials << 'EOF'
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
EOF
chmod 600 ~/.alpaca/credentials
```

---

## Step 4：配置 Slack

1. 创建 Slack App：https://api.slack.com/apps
2. 添加 Bot Token Scopes：`chat:write`, `channels:read`, `channels:history`, `reactions:write`, `files:write`
3. 创建 5 个频道：`#invest-us-market`, `#research`, `#know`, `#ops`, `#advisor`（可选）
4. 将 Bot 邀请进各频道

```bash
# 配置 OpenClaw Slack 集成
openclaw configure --section slack
```

---

## Step 5：部署 Agent 配置

```bash
# 克隆项目
git clone https://github.com/IanLiYi1996/us-stock-investment-team.git
cd us-stock-investment-team

# 运行一键部署脚本
chmod +x setup.sh
./setup.sh
```

脚本会：
- 创建 5 个 Agent workspace（cio/research/ko/ops/advisor）
- 复制 Agent 配置文件（SOUL.md, AGENTS.md, USER.md, MEMORY.md, TASKS.md 等）
- 复制共享规则与模板到所有 workspace
- 创建 KO 知识库目录和 Ops 审计目录
- 复制分析脚本
- 提示你填写频道 ID 和 Alpaca 密钥

---

## Step 6：部署本地搜索引擎（可选但推荐）

```bash
# 使用 Docker 部署 SearXNG
docker run -d \
  --name searxng \
  --restart unless-stopped \
  -p 8888:8888 \
  searxng/searxng

# 验证
curl -s "http://localhost:8888/search?q=AAPL&format=json" | python3 -m json.tool | head -20
```

---

## Step 7：填写频道 ID

编辑 `~/.openclaw/workspace-cio/SOUL.md`，将频道 ID 占位符替换为实际 ID：

```bash
# 获取频道 ID 方法：
# 在 Slack 中右键点击频道 → "View channel details" → 复制 Channel ID

# 编辑 SOUL.md
nano ~/.openclaw/workspace-cio/SOUL.md
```

替换这些占位符：
```
RESEARCH_CHANNEL_ID → 实际的 #research 频道 ID（如 C0AJ5AJQP8S）
KO_CHANNEL_ID       → 实际的 #know 频道 ID
CIO_CHANNEL_ID      → 实际的 #invest-us-market 频道 ID
```

---

## Step 7.5：填写用户画像（推荐）

编辑 `~/.openclaw/workspace-cio/USER.md`，填写你的投资偏好：

```bash
nano ~/.openclaw/workspace-cio/USER.md
```

关键字段：
- 风险承受能力（保守/稳健/积极）
- 投资期限
- 通知频率（每笔交易/每日汇总/仅异常）
- 特殊约束（如"不投烟草股"、"不做空"）

---

## Step 8：配置你的观察清单

```bash
cp config/watchlist.example.yaml ~/.openclaw/workspace-cio/watchlist/watchlist.yaml
# 编辑：替换为你的持仓标的和参数
nano ~/.openclaw/workspace-cio/watchlist/watchlist.yaml
```

---

## Step 9：启动 OpenClaw

```bash
# 启动 OpenClaw 网关
openclaw gateway start

# 验证各 Agent 在线
openclaw status
```

---

## Step 10：启动监控脚本

```bash
# 方式一：手动运行（测试用）
python3 scripts/pre_market_scan.py      # 盘前扫描
python3 scripts/trading_monitor.py     # 盘中监控

# 方式二：守护进程（生产用）
bash scripts/run_monitor.sh &

# 方式三：cron 定时任务
# 编辑 crontab
crontab -e

# 添加以下定时任务（美东时间 UTC-5/UTC-4）
# 盘前扫描（UTC 12:00）
0 12 * * 1-5 python3 /path/to/scripts/pre_market_scan.py

# 盘中监控（UTC 14:30-21:00）
*/30 14-21 * * 1-5 python3 /path/to/scripts/trading_monitor.py
```

---

## 验证安装

```bash
# 测试股票分析脚本
python3 scripts/stock_analysis.py AAPL

# 测试 Alpaca 连接
python3 -c "
from alpaca.trading.client import TradingClient
import os
with open(os.path.expanduser('~/.alpaca/credentials')) as f:
    creds = dict(l.strip().split('=',1) for l in f if '=' in l)
client = TradingClient(creds['ALPACA_API_KEY'], creds['ALPACA_SECRET_KEY'], paper=True)
account = client.get_account()
print(f'✅ Alpaca 连接成功！账户价值: \${account.portfolio_value}')
"
```

---

## 常见问题

**Q: Agent 之间无法通信？**
- 检查 OpenClaw Gateway 是否运行：`openclaw gateway status`
- 确认 Slack Bot 已加入所有目标频道

**Q: Alpaca 交易报错？**
- 确认使用的是 Paper Trading（`paper=True`）
- 检查 API Key 权限是否包含交易权限

**Q: yfinance 获取数据失败？**
- 网络问题：某些地区需要代理
- 尝试：`pip install --upgrade yfinance`
