# 飞书接入指南

## 概述

OpenClaw 支持通过飞书（Feishu/Lark）接入投资团队系统。本文档介绍如何配置飞书作为 Agent 通信平台。

> ⚠️ **重要限制**：飞书的 OpenClaw 插件**不支持 thread（话题）隔离**。同一群组内的对话是扁平的，无法像 Slack 那样用 thread 隔离任务上下文。建议通过"任务驱动的群组分离"来替代。

---

## Step 1：创建飞书应用

1. 前往 [飞书开放平台](https://open.feishu.cn/app) → **创建自建应用**
2. 应用名称：`投资团队 Bot`
3. 记录：
   - **App ID**
   - **App Secret**

---

## Step 2：配置应用能力

### 2.1 开启机器人能力
- 应用能力 → **机器人** → 开启

### 2.2 配置权限
在 **权限管理** 中添加以下权限（可通过批量导入 JSON）：

```
im:message              接收消息
im:message:send         发送消息
im:chat                 获取群信息
im:chat:member          获取群成员
im:resource             上传/下载资源
contact:user.base       获取用户基本信息
```

### 2.3 配置事件订阅
- **事件与回调** → 订阅方式选择 **WebSocket 长连接**
- 添加事件：`im.message.receive_v1`（接收消息事件）

> WebSocket 模式无需公网 IP，适合本地开发和私有部署。

---

## Step 3：创建飞书群组

创建以下群组并将 Bot 添加为成员：

| 群组名 | 用途 | 对应 Agent |
|--------|------|-----------|
| `投资决策` | 交易通知、持仓更新、每日简报 | CIO |
| `调研分析` | 调研报告 | Research |
| `知识沉淀` | 知识更新、策略文档 | KO |
| `系统运维` | 系统审计报告 | Ops |
| `投顾服务` | 投顾数据（可选） | Advisor |

**获取群组 ID：**
- 方法一：通过飞书开放平台 API Explorer 调用 `im/v1/chats` 接口
- 方法二：在群设置中查看群链接，链接中 `oc_` 开头的部分即为 Chat ID
- 格式：`oc_xxxxxxxxxxxxxxxxxxxxxxxx`

---

## Step 4：配置 openclaw.json

复制飞书配置模板并编辑：

```bash
# 如果是全新部署
cp openclaw/feishu.example.json ~/.openclaw/openclaw.json

# 如果已有 Slack/Discord 配置，手动合并 feishu 部分
```

替换以下占位符：

```json
{
  "channels": {
    "feishu": {
      "appId": "YOUR_FEISHU_APP_ID",        // ← App ID
      "appSecret": "YOUR_FEISHU_APP_SECRET"  // ← App Secret
    }
  },
  "routing": [
    {
      "agentId": "cio",
      "match": {
        "channel": "feishu",
        "peer": {
          "kind": "group",
          "id": "oc_xxxxxxxxxxxx"              // ← 投资决策群 ID
        }
      }
    }
  ]
}
```

---

## Step 5：发布应用

1. 在飞书开放平台 → 应用发布 → **创建版本**
2. 提交审核（企业内部应用通常自动通过）
3. 发布后 Bot 即可在群组中接收消息

---

## Step 6：启动与验证

```bash
# 启动 OpenClaw Gateway
openclaw gateway start

# 验证 Agent 状态
openclaw agents list
openclaw status

# 在飞书「投资决策」群中发消息测试
# → "@投资团队Bot 分析一下 AAPL"
```

---

## 飞书特有注意事项

### 无 Thread 隔离（关键限制）
- 飞书群组内的对话是**扁平的**，没有 Slack thread 那样的隔离机制
- **影响**：同一群组中多个并行任务的上下文可能混杂
- **应对策略**：
  1. 每个任务使用简短的锚点消息作为标记
  2. Agent 回复时带任务 ID 前缀：`[TID:20260409-0930] 调研报告...`
  3. 复杂任务考虑创建临时群组隔离

### Bot 消息触发
- 飞书 Bot 接收消息需要 **@提及** 或配置为群组中所有消息可见
- 建议：专用群组设置为"所有消息触发"（在 openclaw.json 中 `requireMention: false`）

### 富文本消息
- 飞书支持 Markdown 消息卡片，适合发送结构化报告
- Agent 可利用飞书消息卡片展示表格、图表等

### 安全建议
- App Secret 不要硬编码在配置文件中
- 建议使用环境变量：`FEISHU_APP_ID` / `FEISHU_APP_SECRET`
- 配置文件权限设置为 600

---

## 与 Slack/Discord 的功能对比

| 功能 | Slack | Discord | 飞书 |
|------|-------|---------|------|
| A2A v2 讨论模式 | ✅ | ❌ | ❌ |
| Thread 隔离 | ✅ | ✅ | ❌ |
| Socket/WebSocket | ✅ | ✅ | ✅ |
| @mention 触发 | ✅ | ✅ | ✅ |
| 文件上传 | ✅ | ✅ | ✅ |
| 消息卡片/富文本 | ✅ | Embed | ✅ (卡片) |
| 企业集成 | 中等 | 低 | ✅ (SSO/审批) |
| 部署复杂度 | 中等 | 较低 | 中等 |

---

## 故障排除

**Q: Bot 加入群组但不回复？**
- 检查事件订阅是否配置了 `im.message.receive_v1`
- 检查 WebSocket 连接是否正常（查看 OpenClaw 日志）
- 确认群组 ID 是否正确（`oc_` 开头）

**Q: 消息内容为空？**
- 检查权限 `im:message` 是否已授权
- 飞书需要发布应用版本后权限才生效

**Q: 多个任务上下文串联？**
- 飞书无 thread 隔离，这是已知限制
- 建议：使用任务 ID 前缀区分，或为复杂任务创建临时群组

**Q: 如何同时使用飞书和 Slack？**
- 在 openclaw.json 中同时配置 `channels.slack` 和 `channels.feishu`
- 同一 Agent 可绑定多个平台的频道/群组
