#!/usr/bin/env python3
"""
Overnight auto-monitor: checks every 5 min for stop-loss/take-profit triggers.
Executes trades automatically per rules:
  - TP: >=8% sell 30%, >=15% sell another 30%, >=25% leave only 10%
  - SL: >=12% cut 50%, >=18% liquidate
"""
import os, time, json, subprocess
from datetime import datetime, timezone, timedelta

# Load Alpaca
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

with open(os.path.expanduser('~/.alpaca/credentials')) as f:
    creds = dict(line.strip().split('=',1) for line in f if '=' in line)
client = TradingClient(creds['ALPACA_API_KEY'], creds['ALPACA_SECRET_KEY'], paper=True)

# Track what we've already sold for take-profit (to handle multi-tier)
# For this session, we track in memory
executed_tp = {}  # symbol -> tier reached (8, 15, 25)
executed_sl = {}  # symbol -> tier reached (12, 18)

LOG_FILE = "/home/ec2-user/.openclaw/workspace-cio/memory/overnight_trades_2026-03-05.log"

def log(msg):
    ts = datetime.now(timezone(timedelta(hours=8))).strftime('%H:%M HKT')
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

def check_and_execute():
    positions = client.get_all_positions()
    clock = client.get_clock()
    
    if not clock.is_open:
        log("Market is closed. Stopping monitor.")
        return False
    
    for pos in positions:
        sym = pos.symbol
        qty = int(float(pos.qty))
        pnl_pct = float(pos.unrealized_plpc) * 100
        cur_price = float(pos.current_price)
        avg_cost = float(pos.avg_entry_price)
        
        # === TAKE PROFIT ===
        if pnl_pct >= 25 and executed_tp.get(sym, 0) < 25:
            # Leave only 10% position
            prev_sold = 0.6 if executed_tp.get(sym, 0) >= 15 else (0.3 if executed_tp.get(sym, 0) >= 8 else 0)
            # We want to keep only 10% of original, sell rest
            sell_qty = max(1, int(qty * 0.9))  # sell 90% of what's left
            if sell_qty > 0 and sell_qty <= qty:
                log(f"🔥 {sym} +{pnl_pct:.1f}% HIT +25% TP! Selling {sell_qty}/{qty} shares (keep 10% floor)")
                req = MarketOrderRequest(symbol=sym, qty=sell_qty, side=OrderSide.SELL, time_in_force=TimeInForce.DAY)
                order = client.submit_order(req)
                log(f"  → Order {order.id}: {order.status}")
                executed_tp[sym] = 25
                
        elif pnl_pct >= 15 and executed_tp.get(sym, 0) < 15:
            # Sell another 30% (cumulative 60%)
            sell_qty = max(1, int(qty * 0.3))
            if sell_qty > 0:
                log(f"🔥 {sym} +{pnl_pct:.1f}% HIT +15% TP! Selling {sell_qty}/{qty} shares (2nd tier)")
                req = MarketOrderRequest(symbol=sym, qty=sell_qty, side=OrderSide.SELL, time_in_force=TimeInForce.DAY)
                order = client.submit_order(req)
                log(f"  → Order {order.id}: {order.status}")
                executed_tp[sym] = 15
                
        elif pnl_pct >= 8 and executed_tp.get(sym, 0) < 8:
            # Sell 30%
            sell_qty = max(1, int(qty * 0.3))
            if sell_qty > 0:
                log(f"🔥 {sym} +{pnl_pct:.1f}% HIT +8% TP! Selling {sell_qty}/{qty} shares (1st tier)")
                req = MarketOrderRequest(symbol=sym, qty=sell_qty, side=OrderSide.SELL, time_in_force=TimeInForce.DAY)
                order = client.submit_order(req)
                log(f"  → Order {order.id}: {order.status}")
                executed_tp[sym] = 8
        
        # === STOP LOSS ===
        if pnl_pct <= -18 and executed_sl.get(sym, 0) < 18:
            log(f"🚨 {sym} {pnl_pct:.1f}% HIT -18% SL! LIQUIDATING {qty} shares")
            req = MarketOrderRequest(symbol=sym, qty=qty, side=OrderSide.SELL, time_in_force=TimeInForce.DAY)
            order = client.submit_order(req)
            log(f"  → Order {order.id}: {order.status}")
            executed_sl[sym] = 18
            
        elif pnl_pct <= -12 and executed_sl.get(sym, 0) < 12:
            sell_qty = max(1, int(qty * 0.5))
            log(f"🚨 {sym} {pnl_pct:.1f}% HIT -12% SL! Cutting {sell_qty}/{qty} shares (50%)")
            req = MarketOrderRequest(symbol=sym, qty=sell_qty, side=OrderSide.SELL, time_in_force=TimeInForce.DAY)
            order = client.submit_order(req)
            log(f"  → Order {order.id}: {order.status}")
            executed_sl[sym] = 12
    
    return True

# Main loop: check every 5 minutes
log("=" * 60)
log("Overnight auto-monitor started. Checking every 5 min.")
log(f"Rules: TP +8%/+15%/+25% | SL -12%/-18%")
log("=" * 60)

# Initial check
positions = client.get_all_positions()
for pos in sorted(positions, key=lambda p: float(p.unrealized_plpc), reverse=True):
    pnl = float(pos.unrealized_plpc) * 100
    flag = "⚡" if pnl >= 7.0 or pnl <= -10.0 else "  "
    log(f"{flag} {pos.symbol}: {pnl:+.1f}% (${float(pos.current_price):.2f})")

while True:
    try:
        should_continue = check_and_execute()
        if not should_continue:
            break
        time.sleep(300)  # 5 minutes
    except KeyboardInterrupt:
        log("Monitor stopped by user.")
        break
    except Exception as e:
        log(f"ERROR: {e}")
        time.sleep(60)

log("Monitor ended.")
