#!/usr/bin/env python3
"""
盘前重大事件扫描脚本
- 美股开盘前(UTC 12:00/13:00)扫描隔夜新闻
- 港股开盘前(UTC 00:30)扫描隔夜新闻
- 生成事件信号文件供开盘调仓脚本读取
"""
import json, time, os, sys
from datetime import datetime, timezone

SIGNALS_FILE = os.path.expanduser("~/.openclaw/workspace-cio/signals/pre-market-signals.json")
LOG_DIR = os.path.expanduser("~/.openclaw/workspace-cio/memory")

# 持仓标的
US_STOCKS = ['NVDA', 'AMZN', 'TSM', 'MU', 'UNH']
HK_STOCKS = [('883','中国海油'), ('700','腾讯'), ('939','建设银行'), ('9618','京东'), ('941','中国移动'), ('2318','中国平安')]

def tavily_search(query, max_results=5):
    import urllib.request
    data = json.dumps({
        "api_key": "YOUR_TAVILY_API_KEY",
        "query": query, "max_results": max_results,
        "search_depth": "advanced", "include_answer": True
    }).encode()
    try:
        req = urllib.request.Request("https://api.tavily.com/search", data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}

def classify_sentiment(text):
    """简单关键词情绪分类"""
    text = text.lower()
    bad = ['crash','plunge','plummet','scandal','fraud','bankrupt','default','war','sanction','ban',
           'sec investigation','downgrade','miss','warning','recall','layoff','ceo resign','sell-off',
           '暴跌','暴雷','造假','制裁','禁令','退市','爆仓','违约','下调','大跌','崩盘','诉讼']
    good = ['surge','soar','beat','upgrade','breakthrough','record','acquisition','buyback','dividend hike',
            'approval','partnership','contract win','ai deal','rally',
            '暴涨','大涨','突破','利好','回购','增持','上调','创新高','超预期','获批']
    
    bad_count = sum(1 for kw in bad if kw in text)
    good_count = sum(1 for kw in good if kw in text)
    
    if bad_count >= 2: return 'very_negative', bad_count
    if bad_count >= 1: return 'negative', bad_count
    if good_count >= 2: return 'very_positive', good_count
    if good_count >= 1: return 'positive', good_count
    return 'neutral', 0

def scan_stock(symbol, name=None):
    """扫描单只股票的最新新闻"""
    display = f"{symbol} ({name})" if name else symbol
    
    # 搜索英文和中文新闻
    queries = [
        f"{symbol} stock news today breaking",
        f"{symbol} earnings announcement latest",
    ]
    if name:
        queries.append(f"{name} 最新消息 重大事件")
    
    all_signals = []
    for q in queries:
        result = tavily_search(q, 3)
        time.sleep(1.5)
        if not result or 'error' in result:
            continue
        
        answer = result.get('answer', '')
        if answer:
            sentiment, score = classify_sentiment(answer)
            if sentiment != 'neutral':
                all_signals.append({
                    'symbol': symbol,
                    'name': name or symbol,
                    'sentiment': sentiment,
                    'score': score,
                    'summary': answer[:300],
                    'query': q
                })
        
        # 也检查每条结果标题
        for r in result.get('results', [])[:3]:
            title = r.get('title', '')
            content = r.get('content', '')[:200]
            combined = f"{title} {content}"
            sentiment, score = classify_sentiment(combined)
            if sentiment != 'neutral':
                all_signals.append({
                    'symbol': symbol,
                    'name': name or symbol,
                    'sentiment': sentiment,
                    'score': score,
                    'summary': f"{title}: {content[:150]}",
                    'url': r.get('url', '')
                })
    
    return all_signals

def scan_macro():
    """扫描宏观/系统性事件"""
    queries = [
        "global market breaking news today geopolitical",
        "Fed interest rate decision latest",
        "美股 港股 重大事件 今日",
        "oil price gold price sharp move today"
    ]
    signals = []
    for q in queries:
        result = tavily_search(q, 3)
        time.sleep(1.5)
        if not result or 'error' in result:
            continue
        answer = result.get('answer', '')
        if answer:
            sentiment, score = classify_sentiment(answer)
            if sentiment != 'neutral':
                signals.append({
                    'symbol': 'MACRO',
                    'name': '宏观事件',
                    'sentiment': sentiment,
                    'score': score,
                    'summary': answer[:300]
                })
    return signals

def generate_action_plan(signals):
    """根据信号生成调仓建议"""
    actions = []
    
    for sig in signals:
        sym = sig['symbol']
        sentiment = sig['sentiment']
        
        if sym == 'MACRO':
            if sentiment == 'very_negative':
                actions.append({
                    'action': 'reduce_all',
                    'pct': 30,
                    'reason': f"宏观重大利空: {sig['summary'][:100]}"
                })
        else:
            if sentiment == 'very_negative':
                actions.append({
                    'action': 'sell',
                    'symbol': sym,
                    'pct': 50,
                    'reason': f"重大利空: {sig['summary'][:100]}"
                })
            elif sentiment == 'negative':
                actions.append({
                    'action': 'reduce',
                    'symbol': sym,
                    'pct': 25,
                    'reason': f"利空信号: {sig['summary'][:100]}"
                })
            elif sentiment == 'very_positive':
                actions.append({
                    'action': 'add',
                    'symbol': sym,
                    'pct': 30,
                    'reason': f"重大利好: {sig['summary'][:100]}"
                })
    
    return actions

def main():
    now = datetime.now(timezone.utc)
    print(f"[{now.strftime('%Y-%m-%d %H:%M UTC')}] 盘前事件扫描开始")
    
    all_signals = []
    
    # 扫描宏观
    print("📡 扫描宏观事件...")
    macro_sigs = scan_macro()
    all_signals.extend(macro_sigs)
    
    # 扫描美股持仓
    print("📡 扫描美股持仓...")
    for sym in US_STOCKS:
        sigs = scan_stock(sym)
        all_signals.extend(sigs)
    
    # 扫描港股持仓
    print("📡 扫描港股持仓...")
    for sym, name in HK_STOCKS:
        sigs = scan_stock(sym, name)
        all_signals.extend(sigs)
    
    # 去重（同一symbol只保留最强信号）
    best = {}
    for sig in all_signals:
        key = sig['symbol']
        if key not in best or sig['score'] > best[key]['score']:
            best[key] = sig
    
    unique_signals = list(best.values())
    
    # 生成调仓计划
    actions = generate_action_plan(unique_signals)
    
    # 保存信号文件
    output = {
        'scan_time': now.isoformat(),
        'signals': unique_signals,
        'actions': actions
    }
    
    os.makedirs(os.path.dirname(SIGNALS_FILE), exist_ok=True)
    with open(SIGNALS_FILE, 'w') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    # 输出结果
    if unique_signals:
        print(f"\n⚡ 发现 {len(unique_signals)} 个事件信号:")
        for sig in unique_signals:
            emoji = "🔴" if 'negative' in sig['sentiment'] else "🟢" if 'positive' in sig['sentiment'] else "⚪"
            print(f"  {emoji} [{sig['sentiment']}] {sig['name']}: {sig['summary'][:80]}")
    else:
        print("\n✅ 未发现重大事件")
    
    if actions:
        print(f"\n📋 生成 {len(actions)} 条调仓建议:")
        for a in actions:
            print(f"  → {a['action']} {a.get('symbol','ALL')} {a['pct']}% | {a['reason'][:80]}")
        print("\nNOTIFY|" + json.dumps(output, ensure_ascii=False))
    else:
        print("\nOK|无需调仓")
    
    # 写日志
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(f"{LOG_DIR}/pre-market-scan.jsonl", 'a') as f:
        f.write(json.dumps(output, ensure_ascii=False) + '\n')

if __name__ == '__main__':
    main()
