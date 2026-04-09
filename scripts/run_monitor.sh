#!/bin/bash
export DISPLAY=:99
export PATH=/home/ec2-user/.local/bin:/usr/local/bin:/usr/bin:$PATH

# 确保IB Gateway在运行
if ! pgrep -f GWClient > /dev/null; then
    echo "IB Gateway not running, starting..."
    pgrep Xvfb || (Xvfb :99 -screen 0 1024x768x24 -ac &)
    sleep 2
    IB_JAVA=/home/ec2-user/.local/share/i4j_jres/Oda-jK0QgTEmVssfllLP/17.0.10.0.101-zulu_64/bin/java
    cd /opt/ibgateway
    $IB_JAVA -cp "/opt/ibgateway/jars/*:/opt/ibc/IBC.jar" \
      -Xmx512m \
      --add-opens=java.base/java.util=ALL-UNNAMED \
      --add-opens=java.desktop/javax.swing=ALL-UNNAMED \
      --add-opens=java.desktop/java.awt=ALL-UNNAMED \
      --add-opens=java.base/java.lang.reflect=ALL-UNNAMED \
      --add-opens=javafx.graphics/com.sun.javafx.application=ALL-UNNAMED \
      -DjtsConfigDir=/opt/ibgateway -Djava.awt.headless=false \
      ibcalpha.ibc.IbcGateway /opt/ibc/config.ini > /tmp/ibgw_restart.log 2>&1 &
    sleep 25
fi

# 运行监控脚本
OUTPUT=$(python3 /home/ec2-user/.openclaw/workspace-cio/scripts/trading_monitor.py 2>&1)

# 如果有交易或警报，通过openclaw发送消息
if echo "$OUTPUT" | grep -q "^NOTIFY|"; then
    MSG=$(echo "$OUTPUT" | grep "^NOTIFY|" | sed 's/^NOTIFY|//')
    openclaw send --channel slack --to "C0AJ5AGUW3C" --message "📊 盘中自动交易通知:\n$MSG" 2>/dev/null || true
fi

echo "$OUTPUT" >> /home/ec2-user/.openclaw/workspace-cio/memory/monitor.log
