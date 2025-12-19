import pandas as pd
import numpy as np
from scipy import stats


def merge_sentiment_volatility(sentiment_df, stock_df, mode='daily'):
    """
    Verbindet Sentiment-Daten mit Volatilitäts-Daten.
    
    Args:
        sentiment_df: DataFrame mit 'ticker', 'date'/'year_week', 'sentiment_score'
        stock_df: DataFrame mit 'Ticker', 'Date', 'Volatility', 'Daily_Return'
        mode: 'daily' oder 'weekly'
    
    Returns:
        Kombinierter DataFrame
    """
    sentiment_df = sentiment_df.copy()
    stock_df = stock_df.copy()
    
    if mode == 'weekly':
        # Wöchentliches Merge
        merged = pd.merge(
            sentiment_df,
            stock_df,
            left_on=['ticker', 'year_week'],
            right_on=['Ticker', 'year_week'],
            how='inner'
        )
        merged['ticker'] = merged['Ticker']
    else:
        # Tägliches Merge
        sentiment_df['date'] = pd.to_datetime(sentiment_df['date']).dt.date
        stock_df['date'] = pd.to_datetime(stock_df['Date']).dt.date
        stock_df['ticker'] = stock_df['Ticker']
        
        merged = pd.merge(
            sentiment_df,
            stock_df[['ticker', 'date', 'Volatility', 'Daily_Return', 'Close']],
            on=['ticker', 'date'],
            how='inner'
        )
    
    return merged


def calculate_correlation(df, col1='sentiment_score', col2='Volatility'):
    """
    Berechnet Pearson-Korrelation zwischen zwei Spalten.
    
    Returns:
        tuple: (correlation, p_value)
    """
    # NaN-Werte entfernen
    clean_df = df[[col1, col2]].dropna()
    
    if len(clean_df) < 3:
        return np.nan, np.nan
    
    # Check ob Werte konstant sind (Standardabweichung = 0)
    if clean_df[col1].std() == 0 or clean_df[col2].std() == 0:
        return 0.0, 1.0  # Keine Korrelation möglich
        
    corr, p_value = stats.pearsonr(clean_df[col1], clean_df[col2])
    return corr, p_value


def calculate_all_correlations(df):
    """
    Berechnet alle relevanten Korrelationen.
    
    Returns:
        Dictionary mit Korrelationsergebnissen
    """
    results = {}
    
    # 1. Sentiment vs Volatilität
    corr, p = calculate_correlation(df, 'sentiment_score', 'Volatility')
    results['sentiment_vs_volatility'] = {'correlation': corr, 'p_value': p}
    
    # 2. Sentiment vs Rendite (zum Vergleich)
    corr, p = calculate_correlation(df, 'sentiment_score', 'Daily_Return')
    results['sentiment_vs_return'] = {'correlation': corr, 'p_value': p}
    
    # 3. Absolutes Sentiment vs Volatilität
    df_temp = df.copy()
    df_temp['abs_sentiment'] = df_temp['sentiment_score'].abs()
    corr, p = calculate_correlation(df_temp, 'abs_sentiment', 'Volatility')
    results['abs_sentiment_vs_volatility'] = {'correlation': corr, 'p_value': p}
    
    return results


def lead_lag_analysis(df, max_lag=5):
    """
    Lead-Lag-Analyse: Korreliert Sentiment(t) mit Volatilität(t+lag).
    
    Args:
        df: DataFrame mit sentiment_score und Volatility
        max_lag: Maximale Verzögerung in Tagen
    
    Returns:
        DataFrame mit Korrelationen pro Lag
    """
    results = []
    
    for ticker in df['ticker'].unique():
        ticker_df = df[df['ticker'] == ticker].sort_values('date').copy()
        
        for lag in range(-max_lag, max_lag + 1):
            # Volatilität um 'lag' Tage verschieben
            ticker_df['Volatility_shifted'] = ticker_df['Volatility'].shift(-lag)
            
            corr, p = calculate_correlation(ticker_df, 'sentiment_score', 'Volatility_shifted')
            
            results.append({
                'ticker': ticker,
                'lag': lag,
                'correlation': corr,
                'p_value': p
            })
    
    return pd.DataFrame(results)


def print_correlation_summary(results):
    """Gibt eine Zusammenfassung der Korrelationen aus."""
    print("=" * 50)
    print("KORRELATIONSANALYSE: Sentiment vs. Marktdaten")
    print("=" * 50)
    
    for name, values in results.items():
        corr = values['correlation']
        p = values['p_value']
        
        # Interpretation
        if abs(corr) < 0.1:
            strength = "keine"
        elif abs(corr) < 0.3:
            strength = "schwache"
        elif abs(corr) < 0.5:
            strength = "moderate"
        else:
            strength = "starke"
        
        sig = "signifikant" if p < 0.05 else "nicht signifikant"
        
        print(f"\n{name}:")
        print(f"  Korrelation: {corr:.4f} ({strength})")
        print(f"  P-Wert: {p:.4f} ({sig})")
    
    print("\n" + "=" * 50)


# Test
if __name__ == "__main__":
    # Beispieldaten erstellen
    np.random.seed(42)
    
    test_df = pd.DataFrame({
        'ticker': ['AAPL'] * 50,
        'date': pd.date_range('2024-01-01', periods=50),
        'sentiment_score': np.random.uniform(-1, 1, 50),
        'Volatility': np.random.uniform(0.01, 0.05, 50),
        'Daily_Return': np.random.uniform(-0.03, 0.03, 50)
    })
    
    print("=== Korrelationsanalyse Test ===\n")
    
    results = calculate_all_correlations(test_df)
    print_correlation_summary(results)
