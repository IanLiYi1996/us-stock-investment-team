# TOOLS — KO 工具参考

## 文件操作

### 决策日志写入
```bash
# 创建决策日志
cat > decisions/YYYY-MM-DD-SYMBOL-ACTION.md << 'EOF'
## [SYMBOL] [YYYY-MM-DD] [BUY/SELL/HOLD]
### 决策摘要
...
EOF
```

### 知识库更新
```bash
# 更新原则
echo "新原则内容" >> knowledge/principles.md

# 更新模式
echo "新模式内容" >> knowledge/patterns.md

# 记录伤疤
echo "新伤疤内容" >> knowledge/scars.md
```

## Markdown 编辑

KO 的核心工具是结构化 Markdown 写作：

### 决策日志模板
参考 `SOUL.md` 中的决策日志格式：
- 决策摘要（操作、原因、信心等级）
- 数据依据（基本面、技术面、催化剂、信息来源）
- 结果追踪（入场价、目标价、止损价、实际结果）
- 学到的教训

### 知识提炼工具
从 Closeout 中提炼知识时，使用以下结构：
```markdown
## [Principle/Pattern/Scar]: [名称]
- **内容**: [一句话描述]
- **来源**: [YYYY-MM-DD 案例]
- **适用边界**: [什么条件下适用]
- **反例**: [什么情况不适用]
- **回滚建议**: [判断错误时如何修正]
```

## A2A 工具

### 通知 CIO
```python
sessions_send(agentId="cio", message="知识已更新: [更新内容摘要]")
```

### 通知 Ops（system-level 变更）
```python
sessions_send(agentId="ops", message="System-level 知识变更: [变更内容]")
```

## 工作目录
```
workspace-ko/
├── knowledge/
│   ├── principles.md    # 投资原则
│   ├── patterns.md      # 验证有效的模式
│   ├── scars.md         # 踩过的坑
│   └── decisions/       # 决策日志
├── inbox/               # 待处理的 closeout
├── MEMORY.md            # 长期精选
└── TASKS.md             # 活跃任务
```
