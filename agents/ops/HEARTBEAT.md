# HEARTBEAT — Ops 自检清单

> 每周一执行（与周度审计同步），紧急情况可手动触发

---

## 周度自检

### 1. 配置一致性
- [ ] CIO SOUL.md 中的止损止盈阈值是否与脚本一致？
  - 对比: `agents/cio/SOUL.md` vs `scripts/trading_monitor.py` vs `scripts/overnight_monitor.py`
- [ ] A2A 权限矩阵是否与 openclaw.json 一致？
- [ ] 各 Agent 的 IDENTITY.md 是否与 openclaw.json 中的 name 一致？

### 2. Self-Update 审计
- [ ] 本周是否有 Agent 进行了 Self-Update？
- [ ] 如有，是否按 SELF_UPDATE_TEMPLATE 记录？
- [ ] 涉及硬性拦截条件的变更是否经过审核？

### 3. 知识质量
- [ ] KO 本周产出的 principle/pattern/scar 质量如何？
- [ ] 每条知识是否包含适用边界和反例？
- [ ] 是否有重复或矛盾的知识条目？

### 4. MEMORY 健康度
- [ ] 各 Agent MEMORY.md 是否有过时条目？
- [ ] 是否有 Agent 的 MEMORY.md 膨胀过快（>50 行）？
- [ ] TASKS.md 中是否有超过 7 天未更新的任务？

### 5. 系统状态
- [ ] OpenClaw gateway 是否正常运行？
- [ ] Cron 任务是否按时执行？
- [ ] 最近 7 天是否有未处理的错误日志？
