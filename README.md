# Sentiment-Analyse und Aktienvolatilität

**Universität:** Hochschule Reutlingen 
**Projekt:** Prüfungsleistung Applied Finance in Python  
**Datum:** Dezember 2025

## Fragestellung

> Hängt das durch FinBERT extrahierte Markt-Sentiment stärker mit der **Volatilität** einer Aktie zusammen als mit der **Kursrichtung**?

## Technologie-Stack

| Komponente | Bibliothek | Zweck |
|------------|-----------|-------|
| **Sentiment-Analyse** | FinBERT (ProsusAI/finbert) | Spezialisiertes NLP-Modell für Finanztexte |
| **Kursdaten** | yfinance | Historische Aktienkurse und News |
| **Analyse** | pandas, numpy, scipy | Datenverarbeitung und Statistik |
| **Visualisierung** | plotly | Interaktive HTML-Plots |

## Projektstruktur

```
LLM Projekt/
├── main.py                     # Hauptprogramm
├── data/
│   ├── stock_fetcher.py        # Kursdaten laden (yfinance)
│   └── news_fetcher.py         # Nachrichten laden
├── sentiment/
│   ├── finbert_analyzer.py     # FinBERT Sentiment-Analyse
│   └── strategy.md             # Dokumentation der Modell-Strategie
├── analysis/
│   ├── volatility.py           # Volatilitätsberechnung
│   └── correlation.py          # Korrelationsanalyse & Lead-Lag
├── visualizations/
│   └── plots.py                # Plotly-Diagramme
└── plots/                      # Output: HTML-Visualisierungen
```

## Installation & Ausführung

### 1. Voraussetzungen
- Python 3.10+
- Virtual Environment aktiviert

### 2. Bibliotheken installieren
```bash
pip install -r requirements.txt
```

Oder manuell:
```bash
pip install pandas python-dotenv yfinance requests feedparser transformers torch plotly scipy numpy
```

### 3. (Optional) API-Keys konfigurieren
Für mehr Datenquellen:
```bash
cp .env.example .env
# Bearbeite .env und füge deine API-Keys ein
```

### 4. Projekt ausführen
```bash
python main.py
```

### 3. Ergebnisse
- **Konsole:** Korrelationsstatistiken
- **plots/ Ordner:** Interaktive HTML-Visualisierungen

## Analysemethoden

### 1. Volatilitätsberechnung
- **Rolling Volatility:** 20-Tage Standardabweichung der Renditen
- **Formel:** $\sigma_{20d} = \text{std}(r_{t-19}, ..., r_t)$

### 2. Korrelationsanalyse
- **Pearson-Korrelation:** Sentiment vs. Volatilität
- **Vergleichsanalyse:** Sentiment vs. Rendite
- **Extremwert-Analyse:** |Sentiment| vs. Volatilität

### 3. Lead-Lag-Analyse
- Prüft, ob Sentiment der Volatilität zeitlich vorausgeht
- Untersucht Lags von -5 bis +5 Tagen

## Unternehmen im Datensatz

- **Tech:** AAPL, MSFT, GOOGL, AMZN, NVDA, TSLA
- **Finanzen:** JPM, V
- **Gesundheit:** JNJ
- **Energie:** XOM

## Interpretation der Ergebnisse

### Erwartete Hypothese
- **Negative Korrelation:** Schlechtes Sentiment → hohe Volatilität (Unsicherheit)
- **Lead-Effekt:** Sentiment sagt Volatilität vorher

### Mögliche Erklärungen
1. **Volatilität ≠ Richtung:** Volatilität misst Unsicherheit, nicht Performance
2. **Markteffizienz:** Sentiment ist bereits im Preis eingepreist
3. **Datenmenge:** Mehr historische Daten könnten Zusammenhänge deutlicher zeigen

## Limitationen

- Yahoo Finance liefert nur ~10 News pro Ticker
- Sentiment basiert nur auf Überschriften (nicht Volltexte)
- Kleine Stichprobe (14-30 Datenpunkte je nach Zeitraum)

## Erweiterungsmöglichkeiten

1. **Mehr Datenquellen:** NewsAPI, Reddit, Twitter
2. **Längerer Zeitraum:** 2-3 Jahre statt 6-12 Monate
3. **Weitere Kennzahlen:** VIX, Optionsvolatilität
4. **Machine Learning:** Random Forest für Volatilitätsprognose

## Autor
Eyas
