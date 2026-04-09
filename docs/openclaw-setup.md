# OpenClaw 配置指南

## 概述

OpenClaw 是驱动整个投资团队的 Agent 框架。你需要：
1. **注册 4 个 Agent**（CIO / Research / KO / Advisor）
2. **绑定 Slack**（Bot Token + 频道路由）
3. **配置定时任务**（盘前扫描、收盘总结、新闻简报）

---

## Step 1：创建 Slack App

### 1.1 创建应用
1. 前往 https://api.slack.com/apps → **Create New App** → **From scratch**
2. App Name: `Investment Team`，选择你的 workspace

### 1.2 配置权限（OAuth & Permissions）
在 **Bot Token Scopes** 中添加：
```
channels:history    读取频道消息历史
channels:read       读取频道列表
chat:write          发送消息
reactions:write     添加 emoji 反应
files:write         上传文件（发图表用）
```

### 1.3 开启 Socket Mode
- **Settings → Socket Mode** → Enable Socket Mode
- 记录生成的 **App-Level Token**（`xapp-` 开头）

### 1.4 安装到 Workspace
- **OAuth & Permissions** → **Install to Workspace**
- 记录生成的 **Bot Token**（`xoxb-` 开头）

---

## Step 2：创建 Slack 频道

在 Slack 中创建以下频道并邀请 Bot：

| 频道名 | 用途 | 对应 Agent |
|--------|------|-----------|
| `#invest-us-market` | 交易通知、持仓更新 | CIO |
| `#research` | 调研报告 | Research |
| `#know` | 知识更新、策略文档 | KO |
| `#advisor`（可选） | 投顾数据 | Advisor |

**获取频道 ID：**
在 Slack 中右键点击频道 → **View channel details** → 底部显示 Channel ID（`C` 开头）

---

## Step 3：配置 openclaw.json

```bash
# 复制配置模板
cp openclaw/openclaw.example.json ~/.openclaw/openclaw.json
```

编辑 `~/.openclaw/openclaw.json`，替换所有占位符：

```json
{
  "channels": {
    "slack": {
      "botToken": "xoxb-YOUR-BOT-TOKEN",          // ← Slack Bot Token
      "appToken": "xapp-YOUR-APP-TOKEN"            // ← Slack App Token
    }
  },
  "routing": [
    { "agentId": "cio",      "match": { "peer": { "id": "C0XXXXXXXXX" } } },  // ← CIO 频道 ID
    { "agentId": "research", "match": { "peer": { "id": "C0YYYYYYYYY" } } },  // ← Research 频道 ID
    { "agentId": "ko",       "match": { "peer": { "id": "C0ZZZZZZZZZ" } } }   // ← KO 频道 ID
  ]
}
```

---

## Step 4：注册 Agent

运行 setup.sh 后，OpenClaw 会自动读取 `openclaw.json` 中的 `agents.list`。
每个 Agent 的 workspace 已由 setup.sh 创建好，配置文件已复制到对应目录。

**验证 Agent 注册：**
```bash
openclaw agents list
```
应看到：
```
✅ cio       - CIO / 投资执行专家       (workspace-cio)
✅ research  - Research / 调研专家      (workspace-research)
✅ ko        - KO / 知识官              (workspace-ko)
✅ advisor   - Advisor / 投顾代理       (workspace-advisor)
```

---

## Step 5：配置定时任务（Cron）

```bash
# 复制 cron 配置模板
cp openclaw/cron/cron.example.json ~/.openclaw/cron/cron.json
```

编辑 `~/.openclaw/cron/cron.json`，将所有 `YOUR_*_CHANNEL_ID` 替换为实际频道 ID。

**默认定时任务（亚洲时区）：**

| 任务名 | 时间（北京时间）| 说明 |
|--------|----------------|------|
| 早间财经新闻简报 | 周一至五 08:00 | 当日开盘前新闻摘要 |
| 盘前市场扫描 | 周一至五 09:30 | 美股开盘前30min事件扫描 |
| 收盘总结 | 周一至五 16:30 | 持仓盈亏 + 当日操作记录 |
| 晚间财经总结 | 周一至五 20:00 | 影响明日的重要新闻 |

**自定义定时任务：**
```bash
# 通过 OpenClaw CLI 添加
openclaw cron add

# 或直接编辑 JSON 文件
nano ~/.openclaw/cron/cron.json
```

---

## Step 6：配置模型

在 `openclaw.json` 的 `agents.defaults.model.primary` 中填写你使用的模型：

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-sonnet-4-5"
      }
    }
  }
}
```

**支持的模型提供商：**
- `anthropic/claude-*`（需要 Anthropic API Key）
- `amazon-bedrock/...`（需要 AWS 配置）
- `openai/gpt-*`（需要 OpenAI API Key）
- 更多参见：https://docs.openclaw.ai/models

---

## Step 7：启动 & 验证

```bash
# 启动 OpenClaw Gateway
openclaw gateway start

# 查看状态
openclaw status
openclaw gateway status

# 查看日志（实时）
openclaw logs --follow

# 测试：在 Slack #invest-us-market 频道发消息
# "@CIO 分析 AAPL"
# → 应收到 CIO 的回复
```

---

## 配置速查

| 文件 | 位置 | 说明 |
|------|------|------|
| 主配置 | `~/.openclaw/openclaw.json` | Agent注册、Slack绑定、路由 |
| 定时任务 | `~/.openclaw/cron/cron.json` | 自动化任务调度 |
| CIO 策略 | `~/.openclaw/workspace-cio/SOUL.md` | 投资策略、止损规则 |
| 持仓清单 | `~/.openclaw/workspace-cio/watchlist/watchlist.yaml` | 目标标的 |
| Alpaca 密钥 | `~/.alpaca/credentials` | 交易 API 密钥 |

---

## 完整配置检查清单

```
□ OpenClaw 已安装 (npm install -g openclaw)
□ openclaw.json 已配置（Slack tokens + 频道 ID）
□ 4 个 Agent workspace 已创建（setup.sh 完成）
□ Alpaca Paper Trading 密钥已配置
□ Slack Bot 已邀请进 4 个频道
□ cron.json 已配置（频道 ID 已替换）
□ openclaw gateway start 已运行
□ 在 Slack 中测试 @CIO 消息可以得到回复
```
