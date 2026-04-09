# Discord 接入指南

## 概述

除 Slack 外，OpenClaw 支持通过 Discord 接入投资团队系统。本文档介绍如何配置 Discord 作为 Agent 通信平台。

> ⚠️ **A2A 限制**：Discord 目前仅支持 A2A v1（委派模式），不支持 A2A v2 的独立 App 讨论模式。跨 Agent 协作通过 `sessions_spawn` 实现。

---

## Step 1：创建 Discord Bot

1. 前往 [Discord Developer Portal](https://discord.com/developers/applications)
2. **New Application** → 命名为 `Investment Team`
3. 进入 **Bot** 页面：
   - 点击 **Reset Token** → 记录 Bot Token
   - ⚠️ **必须开启以下 Privileged Intents**：
     - ✅ Server Members Intent
     - ✅ Presence Intent
     - ✅ **Message Content Intent**（不开启则 Bot 无法读取消息）

---

## Step 2：邀请 Bot 到服务器

1. 进入 **OAuth2 → URL Generator**
2. 选择 Scopes：`bot`
3. 选择 Bot Permissions：
   - View Channels
   - Send Messages
   - Send Messages in Threads
   - Create Public Threads
   - Read Message History
   - Add Reactions
   - Attach Files
4. 复制生成的 URL，在浏览器中打开，选择你的服务器

---

## Step 3：创建 Discord 频道

在 Discord 服务器中创建以下频道：

| 频道名 | 用途 | 对应 Agent |
|--------|------|-----------|
| `#invest-us-market` | 交易通知、持仓更新、每日简报 | CIO |
| `#research` | 调研报告 | Research |
| `#know` | 知识更新、策略文档 | KO |
| `#ops` | 系统审计报告 | Ops |
| `#advisor` | 投顾数据（可选） | Advisor |

**获取频道 ID：**
- 开启 Discord 开发者模式：用户设置 → 高级 → 开发者模式 ✅
- 右键点击频道 → **Copy Channel ID**

**获取 Guild（服务器）ID：**
- 右键点击服务器图标 → **Copy Server ID**

---

## Step 4：配置 openclaw.json

复制 Discord 配置模板并编辑：

```bash
# 如果是全新部署
cp openclaw/discord.example.json ~/.openclaw/openclaw.json

# 如果已有 Slack 配置，手动合并 discord 部分
```

替换以下占位符：

```json
{
  "channels": {
    "discord": {
      "botToken": "YOUR_DISCORD_BOT_TOKEN",   // ← Bot Token
      "guildId": "YOUR_GUILD_ID"               // ← 服务器 ID
    }
  },
  "routing": [
    {
      "agentId": "cio",
      "match": {
        "channel": "discord",
        "peer": {
          "kind": "channel",
          "id": "YOUR_CIO_CHANNEL_ID"          // ← #invest-us-market 频道 ID
        }
      }
    }
  ]
}
```

---

## Step 5：启动与验证

```bash
# 启动 OpenClaw Gateway
openclaw gateway start

# 验证 Agent 状态
openclaw agents list
openclaw status

# 在 Discord #invest-us-market 频道发消息测试
# → "@Investment Team 分析一下 AAPL"
```

---

## Discord 特有注意事项

### Message Content Intent（必须开启）
如果 Bot 无法读取消息内容，99% 是因为未开启 Message Content Intent。
- 路径：Discord Developer Portal → Bot → Privileged Gateway Intents → Message Content Intent ✅
- 需要服务器验证（100+ 服务器才需要 Discord 审批）

### Thread 隔离
- Discord thread 可作为任务隔离单元
- 但 A2A v2 讨论模式在 Discord 上**不可用**（OpenClaw 限制）
- 使用 `sessions_spawn` 替代跨 Agent 协作

### 单 Bot vs 多 Bot
- **推荐：单 Bot 方式**（所有 Agent 共用一个 Bot 身份）
- 多 Bot 方式需要为每个 Agent 创建独立 Discord App，部署复杂度大幅上升

### 频道权限
- 确保 Bot 在所有 5 个频道都有发送消息权限
- 建议为 Bot 创建专用 Role，统一管理权限

---

## 与 Slack 的功能对比

| 功能 | Slack | Discord |
|------|-------|---------|
| A2A v2 讨论模式 | ✅ | ❌ |
| Thread 隔离 | ✅ | ✅ |
| Socket Mode | ✅ | ✅ (WebSocket) |
| @mention 触发 | ✅ | ✅ |
| 文件上传 | ✅ | ✅ |
| Emoji 反应 | ✅ | ✅ |
| 部署复杂度 | 中等 | 较低 |

---

## 故障排除

**Q: Bot 在线但不回复消息？**
- 检查 Message Content Intent 是否开启
- 检查 Bot 是否在目标频道有权限
- 检查 openclaw.json 中的频道 ID 是否正确

**Q: A2A 派单失败？**
- Discord 不支持 A2A v2，确保使用 `sessions_spawn` 而非 `sessions_send`
- 检查 `agentToAgent.allow` 列表是否包含目标 Agent

**Q: 如何同时使用 Slack 和 Discord？**
- 在 openclaw.json 中同时配置 `channels.slack` 和 `channels.discord`
- 每个 Agent 可以绑定多个平台的频道
