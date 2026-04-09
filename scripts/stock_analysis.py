#!/usr/bin/env python3
"""
股票基本面 + 技术面分析工具
用法: python3 stock_analysis.py AAPL LMT XOM
"""
import sys, json, warnings
from datetime import datetime, timedelta
warnings.filterwarnings('ignore')

import yfinance as yf
import pandas as pd
import numpy as np

def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calc_macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast).mean()
    ema_slow = series.ewm(span=slow).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def analyze_stock(symbol):
    """对单只股票进行基本面+技术面分析"""
    result = {"symbol": symbol, "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}
    
    try:
        tk = yf.Ticker(symbol)
        info = tk.info or {}
    except Exception as e:
        result["error"] = f"获取数据失败: {e}"
        return result
    
    # ===== 基本面 =====
    fundamentals = {}
    
    # 估值指标
    fundamentals["price"] = info.get("currentPrice") or info.get("regularMarketPrice")
    fundamentals["market_cap"] = info.get("marketCap")
    fundamentals["pe_trailing"] = info.get("trailingPE")
    fundamentals["pe_forward"] = info.get("forwardPE")
    fundamentals["pb"] = info.get("priceToBook")
    fundamentals["ps"] = info.get("priceToSalesTrailing12Months")
    fundamentals["ev_ebitda"] = info.get("enterpriseToEbitda")
    
    # 成长性
    fundamentals["revenue_growth"] = info.get("revenueGrowth")
    fundamentals["earnings_growth"] = info.get("earningsGrowth")
    fundamentals["earnings_quarterly_growth"] = info.get("earningsQuarterlyGrowth")
    
    # 盈利质量
    fundamentals["profit_margin"] = info.get("profitMargins")
    fundamentals["operating_margin"] = info.get("operatingMargins")
    fundamentals["roe"] = info.get("returnOnEquity")
    fundamentals["roa"] = info.get("returnOnAssets")
    
    # 财务健康
    fundamentals["debt_to_equity"] = info.get("debtToEquity")
    fundamentals["current_ratio"] = info.get("currentRatio")
    fundamentals["free_cash_flow"] = info.get("freeCashflow")
    fundamentals["total_cash"] = info.get("totalCash")
    fundamentals["total_debt"] = info.get("totalDebt")
    
    # 股息
    fundamentals["dividend_yield"] = info.get("dividendYield")
    fundamentals["payout_ratio"] = info.get("payoutRatio")
    
    # 分析师
    fundamentals["target_mean"] = info.get("targetMeanPrice")
    fundamentals["target_low"] = info.get("targetLowPrice")
    fundamentals["target_high"] = info.get("targetHighPrice")
    fundamentals["recommendation"] = info.get("recommendationKey")
    fundamentals["num_analysts"] = info.get("numberOfAnalystOpinions")
    
    # 行业
    fundamentals["sector"] = info.get("sector")
    fundamentals["industry"] = info.get("industry")
    
    result["fundamentals"] = fundamentals
    
    # ===== 技术面 =====
    technicals = {}
    try:
        hist = tk.history(period="1y")
        if hist.empty:
            result["technicals"] = {"error": "无历史数据"}
            return result
        
        close = hist['Close']
        volume = hist['Volume']
        current = close.iloc[-1]
        
        # 均线
        ma20 = close.rolling(20).mean().iloc[-1]
        ma50 = close.rolling(50).mean().iloc[-1]
        ma200 = close.rolling(200).mean().iloc[-1] if len(close) >= 200 else None
        
        technicals["ma20"] = round(ma20, 2)
        technicals["ma50"] = round(ma50, 2)
        technicals["ma200"] = round(ma200, 2) if ma200 else None
        technicals["above_ma20"] = current > ma20
        technicals["above_ma50"] = current > ma50
        technicals["above_ma200"] = (current > ma200) if ma200 else None
        
        # 金叉/死叉
        if ma200:
            ma50_prev = close.rolling(50).mean().iloc[-2]
            ma200_prev = close.rolling(200).mean().iloc[-2] if len(close) >= 201 else None
            if ma200_prev:
                if ma50 > ma200 and ma50_prev <= ma200_prev:
                    technicals["ma_cross"] = "🟢 金叉(近期)"
                elif ma50 < ma200 and ma50_prev >= ma200_prev:
                    technicals["ma_cross"] = "🔴 死叉(近期)"
                elif ma50 > ma200:
                    technicals["ma_cross"] = "多头排列"
                else:
                    technicals["ma_cross"] = "空头排列"
        
        # RSI
        rsi = calc_rsi(close)
        rsi_val = rsi.iloc[-1]
        technicals["rsi_14"] = round(rsi_val, 1)
        if rsi_val > 70:
            technicals["rsi_signal"] = "⚠️ 超买"
        elif rsi_val < 30:
            technicals["rsi_signal"] = "⚠️ 超卖"
        else:
            technicals["rsi_signal"] = "中性"
        
        # MACD
        macd_line, signal_line, histogram = calc_macd(close)
        technicals["macd"] = round(macd_line.iloc[-1], 3)
        technicals["macd_signal"] = round(signal_line.iloc[-1], 3)
        technicals["macd_histogram"] = round(histogram.iloc[-1], 3)
        if histogram.iloc[-1] > 0 and histogram.iloc[-2] <= 0:
            technicals["macd_cross"] = "🟢 MACD金叉"
        elif histogram.iloc[-1] < 0 and histogram.iloc[-2] >= 0:
            technicals["macd_cross"] = "🔴 MACD死叉"
        elif histogram.iloc[-1] > 0:
            technicals["macd_cross"] = "多头"
        else:
            technicals["macd_cross"] = "空头"
        
        # 52周高低
        high_52w = close.max()
        low_52w = close.min()
        technicals["high_52w"] = round(high_52w, 2)
        technicals["low_52w"] = round(low_52w, 2)
        technicals["pct_from_52w_high"] = round((current / high_52w - 1) * 100, 1)
        technicals["pct_from_52w_low"] = round((current / low_52w - 1) * 100, 1)
        
        # 成交量趋势
        vol_20d = volume.tail(20).mean()
        vol_50d = volume.tail(50).mean()
        technicals["avg_volume_20d"] = int(vol_20d)
        technicals["volume_trend"] = "放量" if vol_20d > vol_50d * 1.2 else ("缩量" if vol_20d < vol_50d * 0.8 else "正常")
        
        # 近期涨跌幅
        technicals["chg_1d"] = round((close.iloc[-1] / close.iloc[-2] - 1) * 100, 2) if len(close) >= 2 else None
        technicals["chg_5d"] = round((close.iloc[-1] / close.iloc[-5] - 1) * 100, 2) if len(close) >= 5 else None
        technicals["chg_20d"] = round((close.iloc[-1] / close.iloc[-20] - 1) * 100, 2) if len(close) >= 20 else None
        technicals["chg_60d"] = round((close.iloc[-1] / close.iloc[-60] - 1) * 100, 2) if len(close) >= 60 else None
        
        # 波动率 (20日)
        returns = close.pct_change().tail(20)
        technicals["volatility_20d"] = round(returns.std() * np.sqrt(252) * 100, 1)
        
        # 综合评分
        score = 0
        signals = []
        # 均线
        if technicals.get("above_ma20"): score += 1
        if technicals.get("above_ma50"): score += 1
        if technicals.get("above_ma200"): score += 1
        # RSI
        if 40 <= rsi_val <= 60: score += 1
        elif rsi_val < 30: score += 2; signals.append("超卖反弹机会")
        elif rsi_val > 70: score -= 1; signals.append("超买风险")
        # MACD
        if histogram.iloc[-1] > 0: score += 1
        # 成交量
        if technicals["volume_trend"] == "放量" and technicals.get("chg_5d", 0) > 0:
            score += 1; signals.append("量价齐升")
        
        technicals["tech_score"] = score  # -1 to ~7
        technicals["signals"] = signals
        
    except Exception as e:
        technicals["error"] = str(e)
    
    result["technicals"] = technicals
    
    # ===== 综合判断 =====
    summary = []
    f = result.get("fundamentals", {})
    t = result.get("technicals", {})
    
    price = f.get("price")
    target = f.get("target_mean")
    if price and target:
        upside = (target / price - 1) * 100
        result["analyst_upside_pct"] = round(upside, 1)
        if upside > 15:
            summary.append(f"📈 分析师目标价上行空间 {upside:.1f}%")
        elif upside < -10:
            summary.append(f"📉 分析师目标价下行 {upside:.1f}%")
    
    pe = f.get("pe_forward")
    if pe:
        if pe < 10: summary.append(f"💰 低估值 (Fwd P/E {pe:.1f})")
        elif pe > 40: summary.append(f"⚠️ 高估值 (Fwd P/E {pe:.1f})")
    
    roe = f.get("roe")
    if roe and roe > 0.2:
        summary.append(f"✅ 高ROE ({roe*100:.1f}%)")
    
    tech_score = t.get("tech_score", 0)
    if tech_score >= 5:
        summary.append("🟢 技术面强势")
    elif tech_score <= 1:
        summary.append("🔴 技术面偏弱")
    else:
        summary.append("🟡 技术面中性")
    
    result["summary"] = summary
    
    return result

def format_output(result):
    """格式化输出"""
    sym = result["symbol"]
    print(f"\n{'='*60}")
    print(f"📊 {sym} 分析报告 [{result['timestamp']}]")
    print(f"{'='*60}")
    
    if "error" in result:
        print(f"❌ {result['error']}")
        return
    
    f = result.get("fundamentals", {})
    t = result.get("technicals", {})
    
    # 基本面
    print(f"\n📋 基本面")
    print(f"  价格: ${f.get('price', 'N/A')}")
    print(f"  市值: ${f.get('market_cap', 0)/1e9:.1f}B" if f.get('market_cap') else "  市值: N/A")
    print(f"  行业: {f.get('sector', 'N/A')} / {f.get('industry', 'N/A')}")
    print(f"  —— 估值 ——")
    print(f"  P/E(TTM): {f.get('pe_trailing', 'N/A'):.1f}" if f.get('pe_trailing') else "  P/E(TTM): N/A")
    print(f"  P/E(Fwd): {f.get('pe_forward', 'N/A'):.1f}" if f.get('pe_forward') else "  P/E(Fwd): N/A")
    print(f"  P/B: {f.get('pb', 'N/A'):.2f}" if f.get('pb') else "  P/B: N/A")
    print(f"  EV/EBITDA: {f.get('ev_ebitda', 'N/A'):.1f}" if f.get('ev_ebitda') else "  EV/EBITDA: N/A")
    print(f"  —— 成长性 ——")
    print(f"  营收增长: {f.get('revenue_growth', 0)*100:.1f}%" if f.get('revenue_growth') else "  营收增长: N/A")
    print(f"  盈利增长: {f.get('earnings_growth', 0)*100:.1f}%" if f.get('earnings_growth') else "  盈利增长: N/A")
    print(f"  —— 盈利质量 ——")
    print(f"  利润率: {f.get('profit_margin', 0)*100:.1f}%" if f.get('profit_margin') else "  利润率: N/A")
    print(f"  ROE: {f.get('roe', 0)*100:.1f}%" if f.get('roe') else "  ROE: N/A")
    print(f"  —— 财务健康 ——")
    print(f"  D/E: {f.get('debt_to_equity', 'N/A'):.1f}" if f.get('debt_to_equity') else "  D/E: N/A")
    print(f"  流动比率: {f.get('current_ratio', 'N/A'):.2f}" if f.get('current_ratio') else "  流动比率: N/A")
    print(f"  FCF: ${f.get('free_cash_flow', 0)/1e9:.2f}B" if f.get('free_cash_flow') else "  FCF: N/A")
    print(f"  —— 股息 ——")
    print(f"  股息率: {f.get('dividend_yield', 0)*100:.2f}%" if f.get('dividend_yield') else "  股息率: N/A")
    print(f"  —— 分析师 ——")
    print(f"  目标价: ${f.get('target_low', 'N/A')} ~ ${f.get('target_mean', 'N/A')} ~ ${f.get('target_high', 'N/A')}")
    print(f"  评级: {f.get('recommendation', 'N/A')} ({f.get('num_analysts', 0)}位分析师)")
    
    # 技术面
    print(f"\n📈 技术面")
    if "error" in t:
        print(f"  ❌ {t['error']}")
    else:
        print(f"  —— 均线 ——")
        print(f"  MA20: ${t.get('ma20', 'N/A')} {'✅' if t.get('above_ma20') else '❌'}")
        print(f"  MA50: ${t.get('ma50', 'N/A')} {'✅' if t.get('above_ma50') else '❌'}")
        if t.get('ma200'):
            print(f"  MA200: ${t.get('ma200', 'N/A')} {'✅' if t.get('above_ma200') else '❌'}")
        if t.get('ma_cross'):
            print(f"  均线形态: {t['ma_cross']}")
        print(f"  —— 动量 ——")
        print(f"  RSI(14): {t.get('rsi_14', 'N/A')} {t.get('rsi_signal', '')}")
        print(f"  MACD: {t.get('macd', 'N/A')} / Signal: {t.get('macd_signal', 'N/A')}")
        print(f"  MACD信号: {t.get('macd_cross', 'N/A')}")
        print(f"  —— 价格区间 ——")
        print(f"  52周高: ${t.get('high_52w', 'N/A')} ({t.get('pct_from_52w_high', 'N/A')}%)")
        print(f"  52周低: ${t.get('low_52w', 'N/A')} (+{t.get('pct_from_52w_low', 'N/A')}%)")
        print(f"  —— 涨跌幅 ——")
        for period, key in [("1日", "chg_1d"), ("5日", "chg_5d"), ("20日", "chg_20d"), ("60日", "chg_60d")]:
            val = t.get(key)
            if val is not None:
                print(f"  {period}: {val:+.2f}%")
        print(f"  —— 成交量 ——")
        print(f"  20日均量: {t.get('avg_volume_20d', 0):,}")
        print(f"  量能趋势: {t.get('volume_trend', 'N/A')}")
        print(f"  波动率(年化): {t.get('volatility_20d', 'N/A')}%")
        print(f"  技术评分: {t.get('tech_score', 'N/A')}/7")
        if t.get('signals'):
            print(f"  特殊信号: {', '.join(t['signals'])}")
    
    # 综合
    if result.get("summary"):
        print(f"\n🎯 综合判断")
        for s in result["summary"]:
            print(f"  {s}")
    
    if result.get("analyst_upside_pct") is not None:
        print(f"  分析师目标上行空间: {result['analyst_upside_pct']:+.1f}%")

if __name__ == "__main__":
    symbols = sys.argv[1:] if len(sys.argv) > 1 else ["AAPL"]
    
    for sym in symbols:
        result = analyze_stock(sym.upper())
        format_output(result)
    
    print(f"\n{'='*60}")
    print("⚠️ 以上分析仅供参考，不构成投资建议。投资有风险，决策需谨慎。")
