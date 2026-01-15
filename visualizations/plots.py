import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd


def plot_sentiment_vs_volatility(df, ticker):
    """
    Erstellt einen Dual-Axis Plot: Sentiment vs. Volatilität über die Zeit.
    
    Args:
        df: DataFrame mit 'date', 'sentiment_score', 'Volatility'
        ticker: Ticker-Symbol
    """
    ticker_df = df[df['ticker'] == ticker].sort_values('date')
    
    # Subplot mit 2 y-Achsen erstellen
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # 1. Sentiment (Balken oder Linie)
    fig.add_trace(
        go.Bar(
            x=ticker_df['date'], 
            y=ticker_df['sentiment_score'], 
            name="Sentiment Score",
            marker_color='blue',
            opacity=0.5
        ),
        secondary_y=False,
    )
    
    # 2. Volatilität (Linie)
    fig.add_trace(
        go.Scatter(
            x=ticker_df['date'], 
            y=ticker_df['Volatility'], 
            name="Volatilität (20d)",
            line=dict(color='red', width=2)
        ),
        secondary_y=True,
    )
    
    # Layout anpassen
    fig.update_layout(
        title_text=f"Sentiment vs. Volatilität: {ticker}<br><sub>Zeitreihenanalyse | FinBERT Sentiment-Score & 20-Tage Rolling Volatility</sub>",
        xaxis_title="Datum",
        template="plotly_white"
    )
    
    # Achsenbeschriftungen
    fig.update_yaxes(title_text="Sentiment Score (-1 bis +1)", secondary_y=False, range=[-1.1, 1.1])
    fig.update_yaxes(title_text="Volatilität", secondary_y=True)
    
    return fig


def plot_correlation_scatter(df, ticker=None):
    """
    Erstellt einen Scatterplot: Sentiment vs. Volatilität.
    """
    if ticker:
        plot_df = df[df['ticker'] == ticker]
        title = f"Korrelation: Sentiment vs. Volatilität ({ticker})"
    else:
        plot_df = df
        title = "Korrelation: Sentiment vs. Volatilität (Alle Ticker)"
        
    fig = px.scatter(
        plot_df, 
        x="sentiment_score", 
        y="Volatility", 
        title=title,
        labels={
            "sentiment_score": "Sentiment Score",
            "Volatility": "Volatilität"
        },
        hover_data=['date', 'ticker']
    )
    
    # Optional: Trendlinie würde statsmodels benötigen
    # trendline="ols" wurde entfernt, da nicht installiert
    
    return fig


def plot_lead_lag_heatmap(lead_lag_df):
    """
    Erstellt eine Heatmap für die Lead-Lag-Korrelationen.
    
    Args:
        lead_lag_df: DataFrame aus correlation.lead_lag_analysis
    """
    # Pivot für Heatmap-Format: Index=Ticker, Columns=Lag, Values=Correlation
    pivot_df = lead_lag_df.pivot(index='ticker', columns='lag', values='correlation')
    
    fig = px.imshow(
        pivot_df,
        labels=dict(x="Lag (Tage)", y="Ticker", color="Korrelation"),
        x=pivot_df.columns,
        y=pivot_df.index,
        color_continuous_scale="RdBu_r", # Rot-Blau (Rot=Negativ, Blau=Positiv)
        title="Lead-Lag Korrelation: Sentiment → Volatilität"
    )
    
    return fig
