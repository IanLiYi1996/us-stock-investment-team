# TOOLS — Research

## 新闻数据源（优先级排序）

### 1. SearXNG（首选 — 本地部署）
```bash
curl -s "http://localhost:8888/search?q={query}&format=json&pageno=1" | python3 -c "
import sys,json
d=json.load(sys.stdin)
for r in d.get('results',[])[:5]:
    print(f\"{r['title']}\n  {r['url']}\n  {r.get('content','')[:150]}\n\")
"
```

### 2. Tavily API（备用）
```bash
curl -s -X POST "https://api.tavily.com/search" \
  -H "Content-Type: application/json" \
  -d '{"api_key":"YOUR_TAVILY_KEY","query":"QUERY","max_results":5,"search_depth":"advanced","include_answer":true}'
```

## RSS 财经新闻源

### 国际英文
```python
RSS_FEEDS = {
    "WSJ Markets":      "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
    "FT Home":          "https://www.ft.com/rss/home",
    "Bloomberg":        "https://feeds.bloomberg.com/markets/news.rss",
    "CNBC":             "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114",
    "Reuters":          "https://feeds.reuters.com/reuters/businessNews",
    "Benzinga":         "https://www.benzinga.com/feed",
    "Motley Fool":      "https://www.fool.com/feeds/index.aspx",
    "Economist":        "https://www.economist.com/finance-and-economics/rss.xml",
    "Seeking Alpha":    "https://seekingalpha.com/market_currents.xml",
    "Fed Press":        "https://www.federalreserve.gov/feeds/press_all.xml",
}
```

### 中文财经
```python
CN_FEEDS = {
    "财联社电报": "https://www.cls.cn/nodeapi/updateTelegraphList?app=CailianpressWeb&os=web&sv=8.4.6&rn=30",
    "新浪财经":   "https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2516&k=&num=10&page=1",
    "36氪":       "https://36kr.com/feed",
    "FT中文":     "https://feedx.net/rss/ftchinese.xml",
    "澎湃新闻":   "https://feedx.net/rss/thepaper.xml",
}
```

### RSS 解析代码
```python
import xml.etree.ElementTree as ET, subprocess
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

def fetch_rss(url, hours=12):
    """获取 RSS 并过滤 N 小时内的新闻"""
    data = subprocess.run(['curl','-sL', url,'--max-time','8'],
                          capture_output=True, text=True).stdout
    root = ET.fromstring(data)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    results = []
    for item in root.findall('.//item'):
        pub = item.find('pubDate')
        if pub is not None:
            try:
                dt = parsedate_to_datetime(pub.text)
                if dt < cutoff:
                    continue
            except: pass
        results.append({
            "title": item.find('title').text,
            "link":  item.find('link').text,
            "desc":  (item.find('description') or item.find('summary') or ET.Element('x')).text
        })
    return results
```

## 财务数据
```python
import yfinance as yf

def get_fundamentals(symbol):
    """获取关键基本面指标"""
    tk = yf.Ticker(symbol)
    info = tk.info
    return {
        "price": info.get("currentPrice"),
        "pe": info.get("forwardPE"),
        "market_cap": info.get("marketCap"),
        "revenue_growth": info.get("revenueGrowth"),
        "profit_margin": info.get("profitMargins"),
        "roe": info.get("returnOnEquity"),
        "target_price": info.get("targetMeanPrice"),
        "recommendation": info.get("recommendationKey"),
        "num_analysts": info.get("numberOfAnalystOpinions"),
    }
```

## 情绪分类
```python
def classify_sentiment(text):
    """关键词情绪分类"""
    text = text.lower()
    negative_kw = ['crash','plunge','scandal','fraud','bankrupt','sanction','ban',
                   'downgrade','miss','warning','recall','sell-off','暴跌','暴雷',
                   '制裁','违约','崩盘','诉讼','下调']
    positive_kw = ['surge','soar','beat','upgrade','breakthrough','record','buyback',
                   'approval','partnership','rally','暴涨','利好','回购','增持',
                   '上调','创新高','超预期','获批']
    neg = sum(1 for kw in negative_kw if kw in text)
    pos = sum(1 for kw in positive_kw if kw in text)
    if neg >= 2: return 'very_negative'
    if neg >= 1: return 'negative'
    if pos >= 2: return 'very_positive'
    if pos >= 1: return 'positive'
    return 'neutral'
```
