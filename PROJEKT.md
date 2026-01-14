# Projektstruktur: Sentiment-Analyse und Aktienvolatilität

## 📋 Überblick

Dieses Projekt untersucht den Zusammenhang zwischen dem Markt-Sentiment aus Finanznachrichten und der Aktienvolatilität. Es analysiert, ob Sentiment stärker mit der Volatilität als mit der Kursrichtung korreliert.

---

## 🗂️ Verzeichnisstruktur

```
Sentiment-Analysis/
│
├── main.py                      # Hauptprogramm (Pipeline)
├── requirements.txt             # Python-Abhängigkeiten
├── .env                         # API-Keys (optional)
│
├── data/                        # Datenakquise
│   ├── stock_fetcher.py         # Aktienkurse via yfinance
│   └── news_fetcher.py          # Nachrichten aus mehreren Quellen
│
├── sentiment/                   # Sentiment-Analyse
│   ├── finbert_analyzer.py      # FinBERT-Modell für Sentiment-Scores
│   └── strategy.md              # Dokumentation der Prompt-Strategie
│
├── analysis/                    # Statistische Analyse
│   ├── volatility.py            # Volatilitätsberechnung
│   └── correlation.py           # Korrelations- & Lead-Lag-Analyse
│
├── visualizations/              # Visualisierungen
│   ├── plots.py                 # Plotly-Grafiken
│   └── dashboard.py             # Interaktives Dashboard
│
├── plots/                       # Generierte HTML-Plots
│   ├── index.html               # Dashboard (Einstiegspunkt)
│   ├── *_sentiment_volatility.html
│   ├── *_correlation.html
│   └── lead_lag_heatmap.html
│
└── results_*.csv                # Exportierte Ergebnisse
```

---

## 🔄 Pipeline-Ablauf

Das Hauptprogramm `main.py` führt folgende Schritte aus:

```
┌─────────────────────────────────────────────────────────────┐
│                    1. DATENAKQUISE                          │
├─────────────────────────────────────────────────────────────┤
│  • Aktienkurse: yfinance (10 Unternehmen, 1 Jahr)           │
│  • Nachrichten: Yahoo Finance, NewsAPI, Finnhub, Google     │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 2. SENTIMENT-ANALYSE                        │
├─────────────────────────────────────────────────────────────┤
│  • Modell: FinBERT (ProsusAI/finbert)                       │
│  • Score: P(positiv) - P(negativ) → Wertebereich [-1, +1]   │
│  • Aggregation: Tagesdurchschnitt pro Ticker                │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              3. VOLATILITÄTSBERECHNUNG                      │
├─────────────────────────────────────────────────────────────┤
│  • Rolling Volatility: 20-Tage Standardabweichung           │
│  • Berechnung: σ der täglichen Renditen                     │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    4. ANALYSE                               │
├─────────────────────────────────────────────────────────────┤
│  • Korrelation: Sentiment vs. Volatilität (Pearson)         │
│  • Vergleich: Sentiment vs. Rendite                         │
│  • Extremwerte: |Sentiment| vs. Volatilität                 │
│  • Lead-Lag: Zeitversetzte Korrelation (±5 Tage)            │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 5. VISUALISIERUNG                           │
├─────────────────────────────────────────────────────────────┤
│  • Zeitreihen: Sentiment & Volatilität (Dual-Axis)          │
│  • Scatter-Plots: Korrelationsdarstellung                   │
│  • Heatmap: Lead-Lag-Korrelationen                          │
│  • Dashboard: Interaktive Übersicht (HTML)                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Module im Detail

### 1. `data/stock_fetcher.py`
Lädt Aktienkurse für 10 Unternehmen via **yfinance**:

| Ticker | Unternehmen |
|--------|-------------|
| AAPL   | Apple       |
| MSFT   | Microsoft   |
| GOOGL  | Google      |
| AMZN   | Amazon      |
| NVDA   | NVIDIA      |
| TSLA   | Tesla       |
| JPM    | JPMorgan    |
| V      | Visa        |
| JNJ    | Johnson & Johnson |
| XOM    | ExxonMobil  |

**Funktionen:**
- `fetch_stock_data(ticker, period)` – Einzelner Ticker
- `fetch_all_stocks(tickers, period)` – Alle Ticker

---

### 2. `data/news_fetcher.py`
Sammelt Finanznachrichten aus mehreren Quellen:

| Quelle | API-Key benötigt? |
|--------|-------------------|
| Yahoo Finance | Nein |
| NewsAPI | Ja (optional) |
| Finnhub | Ja (optional) |
| Google News RSS | Nein |

**Funktionen:**
- `fetch_yahoo_news(ticker)` – Yahoo Finance Nachrichten
- `fetch_newsapi(company, api_key)` – NewsAPI.org
- `fetch_finnhub_news(ticker, api_key)` – Finnhub
- `fetch_google_news_rss(query)` – Google News RSS
- `fetch_all_news()` – Kombiniert alle Quellen

---

### 3. `sentiment/finbert_analyzer.py`
Führt Sentiment-Analyse mit **FinBERT** durch:

**Modell:** `ProsusAI/finbert` (auf Finanztexten trainiert)

**Score-Berechnung:**
```
Score = P(positiv) - P(negativ)
```
- Wertebereich: [-1, +1]
- +1 = sehr positiv
- 0 = neutral
- -1 = sehr negativ

**Funktionen:**
- `analyze_sentiment(text)` – Einzelner Text
- `analyze_dataframe(df)` – Batch-Verarbeitung
- `aggregate_daily_sentiment(df)` – Tagesdurchschnitt

---

### 4. `analysis/volatility.py`
Berechnet Volatilitätskennzahlen:

**Rolling Volatility:**
$$\sigma_t = \sqrt{\frac{1}{n-1} \sum_{i=t-n+1}^{t} (r_i - \bar{r})^2}$$

- Fenster: 20 Handelstage
- Basiert auf täglichen Renditen

**Funktionen:**
- `calculate_volatility(df, window)` – Rolling Volatility
- `calculate_volatility_by_ticker(df, window)` – Pro Ticker
- `annualize_volatility(volatility)` – Annualisierung (×√252)

---

### 5. `analysis/correlation.py`
Statistische Analysen:

**Korrelationen:**
1. Sentiment vs. Volatilität (Haupthypothese)
2. Sentiment vs. Rendite (Vergleich)
3. |Sentiment| vs. Volatilität (Extremwerte)

**Lead-Lag-Analyse:**
- Korreliert Sentiment(t) mit Volatilität(t+lag)
- Lags: -5 bis +5 Tage
- Identifiziert mögliche Vorhersagekraft

**Funktionen:**
- `merge_sentiment_volatility()` – Daten zusammenführen
- `calculate_correlation()` – Pearson-Korrelation mit p-Wert
- `lead_lag_analysis()` – Zeitversetzte Korrelation

---

### 6. `visualizations/plots.py`
Erstellt interaktive Plotly-Grafiken:

| Plot | Beschreibung |
|------|--------------|
| `plot_sentiment_vs_volatility()` | Dual-Axis Zeitreihe |
| `plot_correlation_scatter()` | Scatter mit Regression |
| `plot_lead_lag_heatmap()` | Heatmap der Lead-Lag-Korrelationen |

---

### 7. `visualizations/dashboard.py`
Generiert ein interaktives HTML-Dashboard (`plots/index.html`):
- Übersicht aller Ticker
- Statistiken pro Unternehmen
- Navigation zu Einzelplots

---

## 📊 Ausgabedateien

### CSV-Ergebnisse
| Datei | Inhalt |
|-------|--------|
| `results_correlation_per_ticker.csv` | Korrelation pro Unternehmen |
| `results_overall_correlations.csv` | Gesamtkorrelationen |

### HTML-Plots
| Datei | Beschreibung |
|-------|--------------|
| `plots/index.html` | Dashboard (Startseite) |
| `plots/{TICKER}_sentiment_volatility.html` | Zeitreihe pro Ticker |
| `plots/{TICKER}_correlation.html` | Scatter-Plot pro Ticker |
| `plots/lead_lag_heatmap.html` | Lead-Lag-Heatmap |

---

## 🚀 Ausführung

### Installation
```bash
pip install -r requirements.txt
```

### API-Keys konfigurieren (optional)
Erstelle `.env` Datei:
```
NEWSAPI_KEY=dein_newsapi_key
FINNHUB_KEY=dein_finnhub_key
```

### Programm starten
```bash
python main.py
```

### Ergebnisse ansehen
```bash
# Dashboard im Browser öffnen
start plots/index.html
```

---

## 📚 Dokumentation

| Datei | Inhalt |
|-------|--------|
| [README.md](README.md) | Projektübersicht |
| [sentiment/strategy.md](sentiment/strategy.md) | Sentiment-Strategie & Modell-Dokumentation |
| [PROJEKTSTRUKTUR.md](PROJEKTSTRUKTUR.md) | Diese Datei |

---

## 🔧 Technologie-Stack

| Komponente | Technologie |
|------------|-------------|
| Sprache | Python 3.x |
| Kursdaten | yfinance |
| NLP-Modell | FinBERT (transformers) |
| Statistik | scipy, pandas, numpy |
| Visualisierung | Plotly |
| GPU-Support | PyTorch (CUDA) |
