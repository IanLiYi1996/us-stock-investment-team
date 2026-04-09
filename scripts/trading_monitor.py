#!/usr/bin/env python3
"""
美股盘中自动跟踪脚本 - 由cron每30分钟调用
"""
import json, time, os, sys
from datetime import datetime, timezone

def tavily_search(query, max_results=3):
    import urllib.request
    data = json.dumps({
        "api_key": "YOUR_TAVILY_API_KEY",
        "query": query, "max_results": max_results,
        "search_depth": "basic", "include_answer": True
    }).encode()
    try:
        req = urllib.request.Request("https://api.tavily.com/search", data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except: return None

def main():
    from ib_insync import IB, Stock, MarketOrder
    now = datetime.now(timezone.utc)
    print(f"[{now.strftime('%Y-%m-%d %H:%M UTC')}] 盘中检查")
    
    ib = IB()
    try: ib.connect('127.0.0.1', 4002, clientId=2, timeout=10)
    except Exception as e:
        print(f"连接失败: {e}"); return
    
    summary = {i.tag: float(i.value) for i in ib.accountSummary() if i.tag in ['NetLiquidation','AvailableFunds'] and i.currency=='SGD'}
    net_liq = summary.get('NetLiquidation', 0)
    positions = ib.positions()
    if not positions:
        print("无持仓"); ib.disconnect(); return
    
    report, trades = [], []
    for pos in positions:
        sym, qty, avg_cost = pos.contract.symbol, pos.position, pos.avgCost
        if qty <= 0: continue
        contract = Stock(sym, 'SMART', 'USD'); ib.qualifyContracts(contract)
        tk = ib.reqMktData(contract); ib.sleep(2)
        price = tk.last or tk.close or 0
        if price <= 0: ib.cancelMktData(contract); continue
        pnl_pct = (price - avg_cost) / avg_cost * 100
        report.append(f"{sym}: {qty:.0f}股 @${avg_cost:.2f}→${price:.2f} ({pnl_pct:+.1f}%)")
        
        if pnl_pct <= -18:
            t = ib.placeOrder(contract, MarketOrder('SELL', qty)); ib.sleep(3)
            trades.append(f"🔴清仓 {sym} {qty:.0f}股 (亏{pnl_pct:.1f}%)")
        elif pnl_pct <= -12:
            sq = int(qty*0.5)
            if sq>0: ib.placeOrder(contract, MarketOrder('SELL', sq)); ib.sleep(3); trades.append(f"🟡减仓 {sym} {sq}股 (亏{pnl_pct:.1f}%)")
        elif pnl_pct >= 20:
            sq = int(qty*0.3)
            if sq>0: ib.placeOrder(contract, MarketOrder('SELL', sq)); ib.sleep(3); trades.append(f"🟢止盈 {sym} {sq}股 (赚{pnl_pct:.1f}%)")
        ib.cancelMktData(contract)
    
    # 新闻检查
    alerts = {}
    for pos in positions:
        if pos.position <= 0: continue
        r = tavily_search(f"{pos.contract.symbol} stock breaking news"); time.sleep(1)
        if r and r.get('answer'):
            ans = r['answer'].lower()
            for kw in ['crash','plunge','scandal','fraud','ceo resign','sec investigation','暴跌','暴雷']:
                if kw in ans:
                    alerts[pos.contract.symbol] = r['answer'][:150]
                    sq = int(pos.position*0.5)
                    if sq>0:
                        c = Stock(pos.contract.symbol,'SMART','USD'); ib.qualifyContracts(c)
                        ib.placeOrder(c, MarketOrder('SELL', sq)); ib.sleep(3)
                        trades.append(f"📰新闻减仓 {pos.contract.symbol} {sq}股")
                    break
    ib.disconnect()
    
    result = json.dumps({"time": now.isoformat(), "positions": report, "trades": trades, "alerts": alerts}, ensure_ascii=False)
    log_dir = os.path.expanduser("~/.openclaw/workspace-cio/memory")
    os.makedirs(log_dir, exist_ok=True)
    with open(f"{log_dir}/trading-log.jsonl", 'a') as f: f.write(result + '\n')
    
    if trades or alerts: print(f"NOTIFY|{result}")
    else: print(f"OK|" + "; ".join(report))

if __name__ == '__main__': main()
