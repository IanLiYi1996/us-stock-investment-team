# 策略定制指南

## 定制投资策略

### 1. 修改持仓标的

编辑 `agents/cio/SOUL.md` 和 `config/watchlist.example.yaml`：

```yaml
# 按你的投资主题分类
positions:
  ai_theme:
    - NVDA   # GPU 霸主
    - MSFT   # Copilot + Azure
    - GOOGL  # Gemini + Google Cloud

  semiconductor:
    - TSM    # 全球代工龙头
    - AVGO   # AI 网络芯片
    - AMD    # CPU + GPU

  growth:
    - AMZN   # 云+电商
    - META   # 广告+AR
    - PLTR   # AI 数据平台
```

### 2. 调整风险参数

**保守型（低风险）：**
```yaml
risk_rules:
  take_profit:
    - threshold: 0.05   # 盈利 5% 就开始止盈
      pct: 0.30
  stop_loss:
    - threshold: -0.08  # 亏损 8% 就开始止损
      pct: 0.50
    - threshold: -0.12  # 亏损 12% 全清
      action: liquidate
position_limits:
  max_single_position: 0.15  # 单标的最多 15%
```

**激进型（高风险高回报）：**
```yaml
risk_rules:
  take_profit:
    - threshold: 0.15   # 盈利 15% 才开始止盈
      pct: 0.25
  stop_loss:
    - threshold: -0.20  # 能承受更大回撤
      pct: 0.50
position_limits:
  max_single_position: 0.30  # 可以重仓单一标的
```

### 3. 定制投资主题

在 `principles/INVESTMENT_FRAMEWORK.md` 中添加你的投资主题：

```markdown
## 投资主题 1：AI 基础设施浪潮
- 核心逻辑：数据中心资本开支高增长，AI 算力需求 2-3 年内不见顶
- 核心标的：NVDA, TSM, AVGO
- 退出条件：AI 资本开支开始收缩，或出现颠覆性替代技术

## 投资主题 2：消费复苏（自定义）
- 核心逻辑：...
- 核心标的：...
- 退出条件：...
```

---

## 定制 Agent 行为

### 让 CIO 更保守（更多确认）

修改 `agents/cio/SOUL.md` 的自主权部分：
```markdown
## 必须用户确认（更保守版本）
- 任何建仓操作（超过 1000 美元）
- 任何清仓操作
- 单笔超过总资产 10% 的操作
```

### 让 Research 更聚焦

修改 `agents/research/SOUL.md`：
```markdown
## 仅关注以下行业（减少噪音）
- 半导体：NVDA, AMD, TSM, AVGO, MU
- 云计算：AMZN(AWS), MSFT(Azure), GOOGL(GCP)

## 每次调研只输出
- 核心结论（1-2 句）
- 最重要的 3 条信息（不超过）
```

### 让 KO 更简洁

修改 `agents/ko/SOUL.md`：
```markdown
## 决策日志简化模式
- 只记录入场价、出场价、盈亏
- 每月一次策略复盘（而非每周）
```

---

## 多账户策略

如果你管理多个账户（如家庭成员账户），可以为每个账户部署一套：

```bash
# 主账户（CIO 配置）
~/.openclaw/workspace-cio/

# 账户2（复制并修改）
cp -r ~/.openclaw/workspace-cio/ ~/.openclaw/workspace-cio-family/
# 然后修改 SOUL.md 中的标的、仓位、风险参数
```

---

## 常见定制场景

### 场景一：只做 AI 赛道
在 `watchlist.yaml` 中只列 AI 标的，在 `SOUL.md` 中注明"仅投资 AI 相关板块"。

### 场景二：ETF 为主 + 个股补充
在 watchlist 中加入 ETF：
```yaml
etfs:
  - symbol: QQQ   # 纳斯达克 100
  - symbol: SMH   # 半导体 ETF
  - symbol: BOTZ  # 机器人/AI ETF
```

### 场景三：高分红策略
修改进入条件，优先筛选高股息率标的：
```markdown
进入条件：
- 股息率 > 2%
- 连续 10 年分红增长
- 派息比率 < 60%
```
