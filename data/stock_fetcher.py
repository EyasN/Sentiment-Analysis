import yfinance as yf
import pandas as pd

# Die 10 Unternehmen
COMPANIES = {
    'AAPL': 'Apple',
    'MSFT': 'Microsoft',
    'GOOGL': 'Google',
    'AMZN': 'Amazon',
    'NVDA': 'NVIDIA',
    'TSLA': 'Tesla',
    'JPM': 'JPMorgan',
    'V': 'Visa',
    'JNJ': 'Johnson & Johnson',
    'XOM': 'ExxonMobil'
}


def fetch_stock_data(ticker, period="1y"):
    """Holt Kursdaten für einen Ticker."""
    stock = yf.Ticker(ticker)
    df = stock.history(period=period)
    df = df.reset_index()  # Datum als Spalte
    df['Ticker'] = ticker
    df['Company'] = COMPANIES.get(ticker, ticker)
    df['Daily_Return'] = df['Close'].pct_change()
    return df


def fetch_all_stocks(tickers=None, period="1y"):
    """Holt Daten für alle (oder ausgewählte) Unternehmen."""
    if tickers is None:
        tickers = list(COMPANIES.keys())
    
    all_data = []
    for ticker in tickers:
        print(f"Lade {ticker}...")
        df = fetch_stock_data(ticker, period)
        all_data.append(df)
    
    return pd.concat(all_data, ignore_index=True)


# Test
if __name__ == "__main__":
    # Einzelner Ticker testen
    df = fetch_stock_data('AAPL', period='3mo')
    print("=== Apple (3 Monate) ===")
    print(df.head())
    print(f"\nAnzahl Tage: {len(df)}")
    print(f"Spalten: {list(df.columns)}")
