# KNOWLEDGE_PIPELINE（知识沉淀流程）

## 三层工件

### Layer 0: 原始事实（不主动读，需要时回溯）
- OpenClaw会话历史（JSONL）
- 工具调用记录
- 用途：debug/审计/追溯

### Layer 1: Closeout（每任务强制，10-15行）
- 每个A/P/S任务完成时产出
- 包含：产出物链接、决策、下一步、踩坑、signal
- 用途：KO/Ops的主要输入源

### Layer 2: 抽象知识（KO周期性产出）
- Principles（原则）：跨场景适用的指导规则
- Patterns（模式）：验证有效的可复用方法
- Scars（伤疤）：踩过的坑，避免重复
- 用途：长期复用，指导未来决策

## KO工作流

### Signal Score 定义

| Signal | 含义 | KO 动作 |
|--------|------|---------|
| 0 | 日常操作（查价格、看持仓） | 跳过 |
| 1 | 小洞察（单一数据点、小规律） | 仅归档 |
| 2 | 可复用教训（交易失误、验证过的模式、数据源发现） | 提炼至 knowledge/ |
| 3 | 框架级影响（策略修订、重大伤疤、原则变更） | 提炼 + 更新 INVESTMENT_FRAMEWORK.md |

### 输入
- 只读signal≥2的closeout
- 不读全部对话历史（避免淹没）

### 处理
1. 从closeout中识别"可复用认知"
2. 判断是scar/pattern/principle
3. 写入对应文件，必须包含：适用边界、反例、回滚建议

### 输出规则
- 一次最多升级0-2条（硬上限，防止信息过载）
- 每条必须可执行、可验证
- 文风：短、硬、有边界
- 每条知识必须包含：
  - **适用边界**：在什么条件下适用
  - **反例**：什么情况下不适用
  - **回滚建议**：如果判断错误，如何修正

## 存储结构

```
workspace-ko/
├── MEMORY.md              # 长期精选
├── knowledge/
│   ├── principles.md      # 原则
│   ├── patterns.md        # 模式
│   ├── scars.md           # 伤疤
│   └── decisions/         # 重要决策日志
└── inbox/                 # 待处理的closeout
```

## 与Ops的协作

- KO产出的principle/pattern变更 → 如影响系统级 → 通知Ops
- Ops审核后 → 决定是否升级为SYSTEM_RULES
