#!/bin/bash
export DISPLAY=:99
export PATH=~/.local/bin:/usr/local/bin:/usr/bin:$PATH

# 运行监控脚本
OUTPUT=$(python3 ~/.openclaw/workspace-cio/scripts/trading_monitor.py 2>&1)

# 如果有交易或警报，通过openclaw发送消息
if echo "$OUTPUT" | grep -q "^NOTIFY|"; then
    MSG=$(echo "$OUTPUT" | grep "^NOTIFY|" | sed 's/^NOTIFY|//')
    openclaw send --channel slack --to "C0AJ5AGUW3C" --message "📊 盘中自动交易通知:\n$MSG" 2>/dev/null || true
fi

echo "$OUTPUT" >> ~/.openclaw/workspace-cio/memory/monitor.log
