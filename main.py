"""
Hauptprogramm: Sentiment-Analyse und Aktienvolatilität

Dieses Skript führt die gesamte Pipeline aus:
1. Datenakquise (Aktienkurse + Nachrichten)
2. Sentiment-Analyse (FinBERT)
3. Volatilitätsberechnung
4. Korrelationsanalyse
5. Visualisierung
"""

import os
import pandas as pd
from dotenv import load_dotenv

# Eigene Module importieren
from data.stock_fetcher import fetch_all_stocks, COMPANIES
from data.news_fetcher import fetch_all_news
from sentiment.finbert_analyzer import analyze_dataframe, aggregate_daily_sentiment
from analysis.volatility import calculate_volatility_by_ticker
from analysis.correlation import (
    merge_sentiment_volatility, 
    calculate_all_correlations,
    calculate_correlation,
    print_correlation_summary,
    lead_lag_analysis
)
from visualizations.plots import (
    plot_sentiment_vs_volatility, 
    plot_correlation_scatter,
    plot_lead_lag_heatmap
)
from visualizations.dashboard import save_dashboard

# Konfiguration laden (.env Datei für API Keys)
load_dotenv()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")  # Optional
FINNHUB_KEY = os.getenv("FINNHUB_KEY")  # Optional


def main():
    print("=" * 60)
    print("PROJEKT: SENTIMENT-ANALYSE UND AKTIENVOLATILITÄT")
    print("=" * 60)
    
    # 1. DATENAKQUISE
    print("\n--- SCHRITT 1: Datenakquise ---")
    
    # Aktienkurse laden (letztes Jahr für mehr Datenpunkte)
    print("Lade Aktienkurse...")
    stock_df = fetch_all_stocks(period="1y")
    print(f"Aktienkurse geladen: {len(stock_df)} Datensätze")
    
    # Nachrichten laden
    print("\nLade Nachrichten...")
    # Alle Quellen: Yahoo Finance + NewsAPI + Finnhub + Google News
    news_df = fetch_all_news(newsapi_key=NEWSAPI_KEY, finnhub_key=FINNHUB_KEY)
    print(f"Nachrichten geladen: {len(news_df)} Artikel")
    if not news_df.empty:
        null_ts = news_df['timestamp'].isna().sum()
        print(f"  Davon ohne Timestamp: {null_ts}")
        print("  Beispiele:")
        for _, row in news_df.head(3).iterrows():
            print(f"    {row['ticker']} | {row['timestamp']} | {row['title'][:60]}")
    
    if news_df.empty:
        print("Keine Nachrichten gefunden! Abbruch.")
        return

    # 2. SENTIMENT-ANALYSE
    print("\n--- SCHRITT 2: Sentiment-Analyse (FinBERT) ---")
    news_df = analyze_dataframe(news_df)
    
    # Aggregieren auf Tagesbasis
    sentiment_daily = aggregate_daily_sentiment(news_df)
    print(f"Tägliche Sentiment-Werte: {len(sentiment_daily)}")

    # 3. VOLATILITÄT BERECHNEN
    print("\n--- SCHRITT 3: Volatilitätsberechnung ---")
    stock_df = calculate_volatility_by_ticker(stock_df, window=20)
    
    # 4. DATEN ZUSAMMENFÜHREN
    print("\n--- SCHRITT 4: Daten zusammenführen ---")
    merged_df = merge_sentiment_volatility(sentiment_daily, stock_df)
    print(f"Kombinierte Datensätze: {len(merged_df)}")
    
    # Datenpunkte pro Ticker anzeigen
    print("\nDatensätze pro Ticker:")
    for ticker in sorted(merged_df['ticker'].unique()):
        count = len(merged_df[merged_df['ticker'] == ticker])
        status = "✅" if count >= 3 else "⚠️"
        print(f"  {status} {ticker}: {count} Datenpunkte")
    
    if len(merged_df) < 10:
        print("Zu wenige gemeinsame Datenpunkte für eine Analyse!")
        print("Tipp: Erhöhe den Zeitraum oder die Anzahl der Nachrichten.")
        return

    # 5. ANALYSE
    print("\n--- SCHRITT 5: Analyse ---")
    
    # Gesamtkorrelation
    results = calculate_all_correlations(merged_df)
    print_correlation_summary(results)
    
    # Statistik pro Ticker
    print("\n--- Statistik pro Ticker ---")
    ticker_stats = []
    for ticker in merged_df['ticker'].unique():
        ticker_df = merged_df[merged_df['ticker'] == ticker]
        corr, p = calculate_correlation(ticker_df, 'sentiment_score', 'Volatility')
        print(f"{ticker}: Korrelation={corr:.3f}, n={len(ticker_df)} Datenpunkte")
        
        ticker_stats.append({
            'Ticker': ticker,
            'Korrelation_Sentiment_Volatility': corr,
            'P_Value': p,
            'Anzahl_Datenpunkte': len(ticker_df),
            'Durchschnitt_Sentiment': ticker_df['sentiment_score'].mean(),
            'Durchschnitt_Volatility': ticker_df['Volatility'].mean()
        })
    
    # Lead-Lag Analyse
    print("\nFühre Lead-Lag-Analyse durch...")
    lead_lag_results = lead_lag_analysis(merged_df, max_lag=5)
    
    # CSV Export mit besserer Formatierung
    print("\nExportiere Ergebnisse nach Excel...")
    ticker_stats_df = pd.DataFrame(ticker_stats)
    
    # Zahlen auf 4 Dezimalstellen runden
    ticker_stats_df['Korrelation_Sentiment_Volatility'] = ticker_stats_df['Korrelation_Sentiment_Volatility'].round(4)
    ticker_stats_df['P_Value'] = ticker_stats_df['P_Value'].round(4)
    ticker_stats_df['Durchschnitt_Sentiment'] = ticker_stats_df['Durchschnitt_Sentiment'].round(4)
    ticker_stats_df['Durchschnitt_Volatility'] = ticker_stats_df['Durchschnitt_Volatility'].round(6)
    
    # Bessere Spaltennamen
    ticker_stats_df.columns = ['Ticker', 'Korrelation', 'P-Wert', 'Datenpunkte', 'Ø Sentiment', 'Ø Volatilität']
    ticker_stats_df.to_csv('results_correlation_per_ticker.csv', index=False, sep=';', decimal=',')
    
    # Gesamtstatistik
    overall_stats = pd.DataFrame([
        {
            'Analyse': 'Sentiment → Volatilität',
            'Korrelation': round(results['sentiment_vs_volatility']['correlation'], 4),
            'P-Wert': round(results['sentiment_vs_volatility']['p_value'], 4),
            'Interpretation': 'Haupthypothese'
        },
        {
            'Analyse': 'Sentiment → Rendite',
            'Korrelation': round(results['sentiment_vs_return']['correlation'], 4),
            'P-Wert': round(results['sentiment_vs_return']['p_value'], 4),
            'Interpretation': 'Vergleichswert'
        },
        {
            'Analyse': '|Sentiment| → Volatilität',
            'Korrelation': round(results['abs_sentiment_vs_volatility']['correlation'], 4),
            'P-Wert': round(results['abs_sentiment_vs_volatility']['p_value'], 4),
            'Interpretation': 'Extremwert-Analyse'
        }
    ])
    overall_stats.to_csv('results_overall_correlations.csv', index=False, sep=';', decimal=',')
    
    print("  ✓ results_correlation_per_ticker.csv (Ticker-Statistik)")
    print("  ✓ results_overall_correlations.csv (Gesamt-Korrelationen)")
    
    # 6. VISUALISIERUNG
    print("\n--- SCHRITT 6: Visualisierung ---")
    
    # Ordner für Plots erstellen
    if not os.path.exists('plots'):
        os.makedirs('plots')
    
    # Plots für jeden Ticker
    for ticker in merged_df['ticker'].unique():
        # Zeitreihe
        fig1 = plot_sentiment_vs_volatility(merged_df, ticker)
        fig1.write_html(f"plots/{ticker}_sentiment_volatility.html")
        
        # Scatter
        fig2 = plot_correlation_scatter(merged_df, ticker)
        fig2.write_html(f"plots/{ticker}_correlation.html")
    
    # Heatmap für alle
    fig3 = plot_lead_lag_heatmap(lead_lag_results)
    fig3.write_html("plots/lead_lag_heatmap.html")
    
    # Dashboard erstellen mit Statistiken
    print("\nErstelle interaktives Dashboard...")
    ticker_stats_dict = {}
    for ticker in merged_df['ticker'].unique():
        ticker_df = merged_df[merged_df['ticker'] == ticker]
        corr, p = calculate_correlation(ticker_df, 'sentiment_score', 'Volatility')
        ticker_stats_dict[ticker] = {
            'correlation': corr,
            'p_value': p,
            'n_points': len(ticker_df),
            'avg_sentiment': ticker_df['sentiment_score'].mean(),
            'avg_volatility': ticker_df['Volatility'].mean()
        }
    
    dashboard_path = save_dashboard(
        list(merged_df['ticker'].unique()), 
        ticker_stats=ticker_stats_dict
    )
    print(f"  ✓ {dashboard_path}")
    
    print("\n" + "="*60)
    print("✅ FERTIG! Alle Ergebnisse wurden erstellt.")
    print("="*60)
    print("\n📊 DASHBOARD ÖFFNEN:")
    print(f"   Öffne: plots/index.html")
    print("\n📁 Weitere Dateien:")
    print("   • plots/*.html - Einzelne Visualisierungen")
    print("   • results_*.csv - Excel-Tabellen")


if __name__ == "__main__":
    main()
