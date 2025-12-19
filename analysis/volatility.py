import pandas as pd
import numpy as np


def calculate_volatility(df, window=20):
    """
    Berechnet Rolling Volatility (Standardabweichung der Renditen).
    
    Args:
        df: DataFrame mit 'Daily_Return' Spalte
        window: Fenstergröße in Tagen (Standard: 20)
    
    Returns:
        DataFrame mit zusätzlicher 'Volatility' Spalte
    """
    df = df.copy()
    df['Volatility'] = df['Daily_Return'].rolling(window=window).std()
    return df


def calculate_volatility_by_ticker(df, window=20):
    """
    Berechnet Volatility für jeden Ticker separat.
    
    Args:
        df: DataFrame mit mehreren Tickern
        window: Fenstergröße
    
    Returns:
        DataFrame mit Volatility pro Ticker
    """
    result = []
    
    for ticker in df['Ticker'].unique():
        ticker_df = df[df['Ticker'] == ticker].copy()
        ticker_df = ticker_df.sort_values('Date')
        ticker_df['Volatility'] = ticker_df['Daily_Return'].rolling(window=window).std()
        result.append(ticker_df)
    
    return pd.concat(result, ignore_index=True)


def calculate_weekly_volatility(df):
    """
    Berechnet durchschnittliche Volatilität pro Woche.
    
    Args:
        df: DataFrame mit täglichen Daten und Volatility-Spalte
    
    Returns:
        DataFrame mit wöchentlicher Volatilität
    """
    df = df.copy()
    df['Date'] = pd.to_datetime(df['Date'])
    df['year_week'] = df['Date'].dt.strftime('%Y-W%U')
    
    weekly = df.groupby(['Ticker', 'year_week']).agg({
        'Volatility': 'mean',  # Durchschnittliche Volatilität der Woche
        'Daily_Return': 'mean',  # Durchschnittliche Rendite der Woche
        'Close': 'last',  # Schlusskurs am Ende der Woche
        'Date': 'min'  # Erster Tag der Woche
    }).reset_index()
    
    return weekly


def annualize_volatility(volatility, trading_days=252):
    """
    Annualisiert die Volatilität.
    
    Args:
        volatility: Tägliche Volatilität
        trading_days: Handelstage pro Jahr (Standard: 252)
    
    Returns:
        Annualisierte Volatilität
    """
    return volatility * np.sqrt(trading_days)


# Test
if __name__ == "__main__":
    import sys
    sys.path.append('..')
    from data.stock_fetcher import fetch_stock_data
    
    # Apple Daten laden
    df = fetch_stock_data('AAPL', period='6mo')
    
    # Volatilität berechnen
    df = calculate_volatility(df, window=20)
    
    print("=== Apple Volatilität (20-Tage Rolling) ===\n")
    print(df[['Date', 'Close', 'Daily_Return', 'Volatility']].tail(10))
    
    # Annualisierte Volatilität
    latest_vol = df['Volatility'].iloc[-1]
    annual_vol = annualize_volatility(latest_vol)
    print(f"\nAktuelle 20-Tage Volatilität: {latest_vol:.4f}")
    print(f"Annualisiert: {annual_vol:.2%}")
