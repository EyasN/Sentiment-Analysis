import yfinance as yf
import pandas as pd
import time
import requests
import feedparser
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
try:
    from data.stock_fetcher import COMPANIES
except ImportError:
    from stock_fetcher import COMPANIES


def fetch_yahoo_news(ticker):
    """Holt Nachrichten von Yahoo Finance für einen Ticker."""
    stock = yf.Ticker(ticker)
    news_list = []
    
    try:
        news = stock.news
        if not news:
            return []
        
        for item in news:
            # Neues Format: {'id': '...', 'content': {...}}
            content = item.get('content', {})
            
            # Zeitstempel aus pubDate (ISO-String)
            pub_date_str = content.get('pubDate')
            if pub_date_str:
                try:
                    ts = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
                except:
                    ts = datetime.now()
            else:
                ts = datetime.now()

            news_item = {
                'ticker': ticker,
                'company': COMPANIES.get(ticker, ticker),
                'title': content.get('title', ''),
                'publisher': content.get('provider', {}).get('displayName', ''),
                'link': content.get('canonicalUrl', {}).get('url', ''),
                'timestamp': ts,
            }
            news_list.append(news_item)
    except Exception as e:
        print(f"Fehler bei {ticker}: {e}")
    
    return news_list


def fetch_newsapi(company_name, api_key, days_back=30):
    """
    Holt Nachrichten von NewsAPI.org
    
    Args:
        company_name: Unternehmensname zum Suchen
        api_key: NewsAPI API-Key
        days_back: Tage in die Vergangenheit (max 30 für Free Tier)
    """
    if not api_key or api_key == "dein_api_key_hier":
        return []
    
    base_url = "https://newsapi.org/v2/everything"
    
    from_date = (datetime.now() - timedelta(days=min(days_back, 29))).strftime('%Y-%m-%d')
    to_date = datetime.now().strftime('%Y-%m-%d')
    
    params = {
        'q': company_name,
        'from': from_date,
        'to': to_date,
        'language': 'en',
        'sortBy': 'publishedAt',
        'pageSize': 50,
        'apiKey': api_key
    }
    
    news_list = []
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        data = response.json()
        
        if data.get('status') == 'ok':
            for article in data.get('articles', []):
                try:
                    ts = datetime.fromisoformat(
                        article.get('publishedAt', '').replace('Z', '+00:00')
                    )
                except:
                    continue
                
                news_item = {
                    'title': article.get('title', ''),
                    'publisher': article.get('source', {}).get('name', ''),
                    'link': article.get('url', ''),
                    'timestamp': ts,
                }
                news_list.append(news_item)
    except Exception as e:
        print(f"  NewsAPI Fehler: {e}")
    
    return news_list


def fetch_finnhub(ticker, api_key, days_back=365):
    """Holt Nachrichten von Finnhub.io"""
    if not api_key or api_key == "dein_api_key_hier":
        return []
    
    from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    to_date = datetime.now().strftime('%Y-%m-%d')
    
    url = f"https://finnhub.io/api/v1/company-news"
    params = {
        'symbol': ticker,
        'from': from_date,
        'to': to_date,
        'token': api_key
    }
    
    news_list = []
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        for article in data:
            try:
                ts = datetime.fromtimestamp(article.get('datetime', 0))
            except:
                continue
            
            news_item = {
                'title': article.get('headline', ''),
                'publisher': article.get('source', ''),
                'link': article.get('url', ''),
                'timestamp': ts,
            }
            news_list.append(news_item)
    except Exception as e:
        print(f"  Finnhub Fehler: {e}")
    
    return news_list


def fetch_google_news(company_name, ticker, days_back=365):
    """Holt Nachrichten von Google News RSS"""
    query = company_name.replace(' ', '+')
    url = f"https://news.google.com/rss/search?q={query}+stock&hl=en-US&gl=US&ceid=US:en"
    
    news_list = []
    
    try:
        feed = feedparser.parse(url)
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        for entry in feed.entries[:50]:  # Limit to 50 articles
            try:
                ts = datetime(*entry.published_parsed[:6])
                if ts < cutoff_date:
                    continue
            except:
                ts = datetime.now()
            
            news_item = {
                'title': entry.get('title', ''),
                'publisher': entry.get('source', {}).get('title', 'Google News'),
                'link': entry.get('link', ''),
                'timestamp': ts,
            }
            news_list.append(news_item)
    except Exception as e:
        print(f"  Google News Fehler: {e}")
    
    return news_list


def fetch_ticker_news(ticker, company_name, newsapi_key, finnhub_key):
    """Holt Nachrichten für einen Ticker aus allen Quellen (parallel ausführbar)."""
    ticker_news = []
    
    # 1. Yahoo Finance
    yahoo_news = fetch_yahoo_news(ticker)
    for item in yahoo_news:
        item['source'] = 'yahoo'
    ticker_news.extend(yahoo_news)
    yahoo_count = len(yahoo_news)
    
    # 2. NewsAPI (wenn Key vorhanden)
    newsapi_count = 0
    if newsapi_key and newsapi_key != "dein_api_key_hier":
        search_name = company_name.split()[0]
        newsapi_news = fetch_newsapi(search_name, newsapi_key, days_back=365)
        for item in newsapi_news:
            item['ticker'] = ticker
            item['company'] = company_name
            item['source'] = 'newsapi'
        ticker_news.extend(newsapi_news)
        newsapi_count = len(newsapi_news)
    
    # 3. Finnhub (wenn Key vorhanden)
    finnhub_count = 0
    if finnhub_key and finnhub_key != "dein_api_key_hier":
        finnhub_news = fetch_finnhub(ticker, finnhub_key, days_back=365)
        for item in finnhub_news:
            item['ticker'] = ticker
            item['company'] = company_name
            item['source'] = 'finnhub'
        ticker_news.extend(finnhub_news)
        finnhub_count = len(finnhub_news)
    
    # 4. Google News RSS
    google_news = fetch_google_news(company_name, ticker, days_back=365)
    for item in google_news:
        item['ticker'] = ticker
        item['company'] = company_name
        item['source'] = 'google'
    ticker_news.extend(google_news)
    google_count = len(google_news)
    
    return ticker, ticker_news, (yahoo_count, newsapi_count, finnhub_count, google_count)


def fetch_all_news(tickers=None, newsapi_key=None, finnhub_key=None):
    """Holt Nachrichten für alle Unternehmen aus ALLEN Quellen (parallel)."""
    if tickers is None:
        tickers = list(COMPANIES.keys())
    
    all_news = []
    
    # Parallel alle Tickers abfragen (10 Threads = 1 pro Ticker)
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {}
        for ticker in tickers:
            company_name = COMPANIES.get(ticker, ticker)
            future = executor.submit(fetch_ticker_news, ticker, company_name, newsapi_key, finnhub_key)
            futures[future] = ticker
        
        # Ergebnisse sammeln
        for future in as_completed(futures):
            ticker = futures[future]
            try:
                ticker, ticker_news, counts = future.result()
                yahoo_c, newsapi_c, finnhub_c, google_c = counts
                all_news.extend(ticker_news)
                
                print(f"✓ {ticker}: Yahoo={yahoo_c} | NewsAPI={newsapi_c} | Finnhub={finnhub_c} | Google={google_c}")
            except Exception as e:
                print(f"✗ {ticker}: Fehler - {e}")
    
    # Zu DataFrame konvertieren
    df = pd.DataFrame(all_news)
    
    if not df.empty:
        # Timezone-aware und timezone-naive Timestamps vereinheitlichen
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True).dt.tz_localize(None)
        df['date'] = df['timestamp'].dt.date
        df = df.dropna(subset=['date'])
        # Duplikate entfernen (gleicher Titel am selben Tag)
        df = df.drop_duplicates(subset=['ticker', 'title', 'date'], keep='first')
        df = df.sort_values('timestamp', ascending=False)
    
    return df


# Test
if __name__ == "__main__":
    # Einzelner Ticker testen
    news = fetch_yahoo_news('AAPL')
    print(f"=== Apple News ({len(news)} Artikel) ===\n")
    
    for item in news[:3]:
        print(f"• {item['title']}")
        print(f"  Quelle: {item['publisher']}")
        print(f"  Datum: {item['timestamp']}")
        print()