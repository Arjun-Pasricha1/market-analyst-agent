import asyncio
import httpx
import feedparser
from datetime import datetime
from typing import Any, List, Dict
from langchain_core.tools import tool

# Keep your FEEDS dictionary here (I'll keep it shortened for this example)
FEEDS ={# ── Indian Sources ────────────────────────────────────────────────────────
    "moneycontrol": {
        "name": "MoneyControl",
        "region": "india",
        "urls": {
            "latest":       "https://www.moneycontrol.com/rss/latestnews.xml",
            "markets":      "https://www.moneycontrol.com/rss/marketreports.xml",
            "stocks":       "https://www.moneycontrol.com/rss/buzzingstocks.xml",
            "economy":      "https://www.moneycontrol.com/rss/economy.xml",
            "ipo":          "https://www.moneycontrol.com/rss/ipoNews.xml",
        },
    },
    "economic_times": {
        "name": "Economic Times",
        "region": "india",
        "urls": {
            "markets":      "https://economictimes.indiatimes.com/markets/rss.cms",
            "stocks":       "https://economictimes.indiatimes.com/markets/stocks/rss.cms",
            "economy":      "https://economictimes.indiatimes.com/economy/rss.cms",
            "latest":       "https://economictimes.indiatimes.com/rssfeedsdefault.cms",
            "mutual_funds": "https://economictimes.indiatimes.com/mf/rss.cms",
        },
    },
    "mint": {
        "name": "Mint",
        "region": "india",
        "urls": {
            "latest":       "https://www.livemint.com/rss/news",
            "markets":      "https://www.livemint.com/rss/markets",
            "economy":      "https://www.livemint.com/rss/economy",
            "companies":    "https://www.livemint.com/rss/companies",
        },
    },
    "business_today": {
        "name": "Business Today",
        "region": "india",
        "urls": {
            "latest":       "https://www.businesstoday.in/rss/home",
            "markets":      "https://www.businesstoday.in/rss/markets",
            "economy":      "https://www.businesstoday.in/rss/economy",
        },
    },
    "financial_express": {
        "name": "Financial Express",
        "region": "india",
        "urls": {
            "latest":       "https://www.financialexpress.com/feed/",
            "market":       "https://www.financialexpress.com/market/feed/",
        },
    },
    "ndtv_profit": {
        "name": "NDTV Profit",
        "region": "india",
        "urls": {
            "latest":       "https://feeds.feedburner.com/ndtvprofit-latest",
            "markets":      "https://feeds.feedburner.com/ndtvprofit-markets",
        },
    },
    "hindu_businessline": {
        "name": "Hindu BusinessLine",
        "region": "india",
        "urls": {
            "latest":       "https://www.thehindubusinessline.com/feeder/default.rss",
            "markets":      "https://www.thehindubusinessline.com/markets/feeder/default.rss",
            "economy":      "https://www.thehindubusinessline.com/economy/feeder/default.rss",
        },
    },
    "zeebiz": {
        "name": "Zee Business",
        "region": "india",
        "urls": {
            "latest":       "https://www.zeebiz.com/rss",
        },
    },

    # ── Global Sources ────────────────────────────────────────────────────────
    "reuters": {
        "name": "Reuters",
        "region": "global",
        "urls": {
            "business":     "https://feeds.reuters.com/reuters/businessNews",
            "markets":      "https://feeds.reuters.com/reuters/companyNews",
            "economy":      "https://feeds.reuters.com/news/economy",
        },
    },
    "bloomberg": {
        "name": "Bloomberg",
        "region": "global",
        "urls": {
            "markets":      "https://feeds.bloomberg.com/markets/news.rss",
            "technology":   "https://feeds.bloomberg.com/technology/news.rss",
            "politics":     "https://feeds.bloomberg.com/politics/news.rss",
        },
    },
    "cnbc": {
        "name": "CNBC",
        "region": "global",
        "urls": {
            "latest":       "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114",
            "markets":      "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=15839135",
            "investing":    "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=15839069",
        },
    },
    "marketwatch": {
        "name": "MarketWatch",
        "region": "global",
        "urls": {
            "latest":       "https://feeds.marketwatch.com/marketwatch/realtimeheadlines/",
            "markets":      "https://feeds.marketwatch.com/marketwatch/marketpulse/",
            "economy":      "https://feeds.marketwatch.com/marketwatch/economy-politics/",
        },
    },
    "forbes": {
        "name": "Forbes",
        "region": "global",
        "urls": {
            "investing":    "https://www.forbes.com/investing/feed2/",
            "business":     "https://www.forbes.com/business/feed2/",
        },
    },
    "ft": {
        "name": "Financial Times",
        "region": "global",
        "urls": {
            "latest":       "https://www.ft.com/rss/home/uk",
            "markets":      "https://www.ft.com/rss/markets",
        },
    },
}
def _parse_feed(source_key: str, category: str, raw: str) -> List[Dict]:
    """Parse raw RSS XML into a clean list of articles."""
    source_meta = FEEDS.get(source_key, {})
    feed = feedparser.parse(raw)
    articles = []
    for entry in feed.entries:
        published = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            try:
                published = datetime(*entry.published_parsed[:6]).isoformat()
            except Exception:
                published = entry.get("published", None)
        
        articles.append({
            "title": entry.get("title", "").strip(),
            "link": entry.get("link", ""),
            "summary": entry.get("summary", entry.get("description", "")).strip()[:300],
            "published": published,
            "source": source_meta.get("name", source_key),
            "region": source_meta.get("region", "global"),
            "category": category,
        })
    return articles
    # Copy your entire FEEDS dict here
async def _fetch_feed(client: httpx.AsyncClient, source_key: str, category: str, url: str) -> List[Dict]:
    """Fetches a single feed and returns parsed articles."""
    try:
        resp = await client.get(url, timeout=10)
        resp.raise_for_status()
        return _parse_feed(source_key, category, resp.text)
    except Exception:
        return []

async def fetch_news_by_keyword(keyword: str, region: str = "all") -> Dict[str, Any]:
    """Concurrent fetcher that filters results by keyword."""
    selected = {k: v for k, v in FEEDS.items() if region == "all" or v["region"] == region}
    tasks = []
    async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0"}, follow_redirects=True) as client:
        for source_key, source_meta in selected.items():
            url = list(source_meta["urls"].values())[0] # Fallback to first URL
            tasks.append(_fetch_feed(client, source_key, "latest", url))
        results = await asyncio.gather(*tasks)

    all_articles = [art for sublist in results for art in sublist]
    keyword_lower = keyword.lower()
    filtered = [a for a in all_articles if keyword_lower in a["title"].lower() or keyword_lower in a["summary"].lower()]
    return {"articles": filtered[:10]} # Limit to 10 for AI efficiency

# ── 3. The LangChain Tool Wrapper ──────────────────────────────────────────
@tool
def get_company_news(query: str, region: str = "all") -> str:
    """
    Searches for the latest financial news about a specific company or stock ticker.
    Args:
        query: Company name or ticker (e.g., 'Reliance', 'TCS', 'Apple').
        region: 'india', 'global', or 'all'. Defaults to 'all'.
    """
    # Helper to run the async logic in the synchronous LangGraph environment
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # If we are already in an event loop (like FastAPI), we need a different approach
        import nest_asyncio
        nest_asyncio.apply()
        
    data = asyncio.run(fetch_news_by_keyword(query, region))
    
    if not data["articles"]:
        return f"No recent news found for '{query}'."
    
    formatted = []
    for art in data["articles"][:5]:
        formatted.append(f"Source: {art['source']}\nTitle: {art['title']}\nSummary: {art['summary']}\nLink: {art['link']}")
    
    return "\n---\n".join(formatted)

    


