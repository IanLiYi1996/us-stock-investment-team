# TOOLS — Ops 工具参考

## 审计工具

### 文件对比（检查配置漂移）
```bash
# 对比 SOUL.md 当前版本与 git 历史
diff <(git show HEAD~1:agents/cio/SOUL.md) agents/cio/SOUL.md

# 检查止损阈值一致性
grep -n "止损\|止盈\|stop.loss\|take.profit" agents/cio/SOUL.md scripts/trading_monitor.py scripts/overnight_monitor.py
```

### Self-Update 审计
```bash
# 查找最近的 Self-Update 记录
find ~/.openclaw/workspace-*/memory/ -name "*.md" -newer /tmp/last_audit -exec grep -l "Self-Update" {} \;
```

### MEMORY 去重检查
```bash
# 检查各 Agent MEMORY.md 中是否有重复条目
for ws in ~/.openclaw/workspace-*/MEMORY.md; do
  echo "=== $ws ==="
  sort "$ws" | uniq -d
done
```

## 报告生成

### 周度审计报告模板
```markdown
## Ops 周度审计: [YYYY-MM-DD]
- **范围**: 本周 S 类 closeout + Self-Update + 阈值检查
- **审计项数**: [N]
- **发现问题**: [N] 条
- **行动项**:
  1. [问题] → [建议] → [负责人]
- **系统健康度**: ✅/⚠️/❌
```

## 五维评估工具

对每个审计项使用以下打分：

| 维度 | 检查方法 |
|------|---------|
| 规则对齐 | 对比变更内容与 SYSTEM_RULES.md |
| 范围影响 | 检查是否影响其他 Agent 的 SOUL/AGENTS |
| 可回滚性 | 确认 Self-Update 中有回滚方案 |
| 资源成本 | 评估变更是否增加系统复杂度 |
| 安全性 | 检查是否涉及交易规则或权限变更 |

## A2A 工具

### 通知相关 Agent
```python
# 审计发现问题时通知
sessions_send(agentId="cio", message="Ops 审计发现: [问题描述]，建议: [修正建议]")
```
