"""
Dashboard Generator - Erstellt eine interaktive HTML-Übersichtsseite
"""
import os


def create_dashboard(tickers, ticker_stats=None):
    """
    Erstellt ein HTML-Dashboard mit Navigation zwischen Ticker-Plots.
    
    Args:
        tickers: Liste der Ticker-Symbole
        ticker_stats: Dictionary mit Statistiken pro Ticker (optional)
    """
    
    html_content = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sentiment-Analyse Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .nav {
            background: #f8f9fa;
            padding: 20px;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
            border-bottom: 2px solid #e9ecef;
        }
        
        .nav-btn {
            padding: 12px 25px;
            background: white;
            border: 2px solid #667eea;
            color: #667eea;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .nav-btn:hover {
            background: #667eea;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .nav-btn.active {
            background: #667eea;
            color: white;
        }
        
        .content {
            padding: 30px;
        }
        
        .ticker-section {
            display: none;
        }
        
        .ticker-section.active {
            display: block;
            animation: fadeIn 0.5s ease;
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .ticker-title {
            color: #667eea;
            font-size: 2em;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .plot-container {
            margin-bottom: 40px;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        iframe {
            width: 100%;
            height: 600px;
            border: none;
        }
        
        .plot-label {
            background: #f8f9fa;
            padding: 15px;
            font-weight: 600;
            color: #495057;
            border-bottom: 2px solid #e9ecef;
        }
        
        .overview-section {
            display: none;
        }
        
        .overview-section.active {
            display: block;
            animation: fadeIn 0.5s ease;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .stat-card h3 {
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 10px;
        }
        
        .stat-card .value {
            font-size: 2.5em;
            font-weight: bold;
        }
        
        .footer {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #6c757d;
            border-top: 2px solid #e9ecef;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Sentiment-Analyse Dashboard</h1>
            <p>Zusammenhang zwischen Markt-Sentiment und Aktienvolatilität</p>
        </div>
        
        <div class="nav">
            <button class="nav-btn active" onclick="showSection('overview')">📈 Übersicht</button>
"""
    
    # Buttons für jeden Ticker
    for ticker in tickers:
        html_content += f'            <button class="nav-btn" onclick="showSection(\'{ticker}\')">{ticker}</button>\n'
    
    html_content += """        </div>
        
        <div class="content">
            <!-- Übersichts-Sektion -->
            <div id="overview" class="overview-section active">
                <h2 class="ticker-title">🎯 Projekt-Übersicht</h2>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>Analysierte Unternehmen</h3>
                        <div class="value">""" + str(len(tickers)) + """</div>
                    </div>
                    <div class="stat-card">
                        <h3>Sentiment-Modell</h3>
                        <div class="value" style="font-size: 1.5em;">FinBERT</div>
                    </div>
                    <div class="stat-card">
                        <h3>Datenquelle</h3>
                        <div class="value" style="font-size: 1.5em;">Yahoo Finance</div>
                    </div>
                </div>
                
                <div class="plot-container">
                    <div class="plot-label">🔥 Lead-Lag Heatmap (Alle Ticker)</div>
                    <iframe src="lead_lag_heatmap.html"></iframe>
                </div>
                
                <div style="background: #f8f9fa; padding: 30px; border-radius: 10px; margin-top: 30px;">
                    <h3 style="color: #667eea; margin-bottom: 15px;">📋 Hinweise zur Interpretation</h3>
                    <ul style="line-height: 2; color: #495057;">
                        <li><strong>Sentiment vs. Volatilität:</strong> Zeigt zeitlichen Verlauf beider Kennzahlen</li>
                        <li><strong>Korrelations-Scatterplot:</strong> Visualisiert den direkten Zusammenhang</li>
                        <li><strong>Lead-Lag Heatmap:</strong> Negative Lags = Sentiment geht Volatilität voraus</li>
                        <li><strong>Interpretation:</strong> Starke Korrelation bei Lag -1/-2 deutet auf Frühindikator hin</li>
                    </ul>
                </div>
            </div>
"""
    
    # Sektionen für jeden Ticker
    for ticker in tickers:
        # Statistiken für diesen Ticker
        stats_html = ""
        if ticker_stats and ticker in ticker_stats:
            stats = ticker_stats[ticker]
            corr = stats.get('correlation', 0)
            p_val = stats.get('p_value', 1)
            n = stats.get('n_points', 0)
            avg_sent = stats.get('avg_sentiment', 0)
            avg_vol = stats.get('avg_volatility', 0)
            
            # Prüfen ob genug Daten vorhanden sind
            import math
            if math.isnan(corr) or n < 3:
                # Zu wenige Datenpunkte
                stats_html = f"""
                <div style="background: #fff3cd; padding: 20px; border-radius: 10px; margin-bottom: 30px; border: 2px solid #ffc107;">
                    <h3 style="color: #856404; margin-bottom: 15px;">⚠️ Unzureichende Daten für {ticker}</h3>
                    <p style="color: #856404; margin-bottom: 10px;">
                        <strong>Nur {n} Datenpunkt(e) verfügbar.</strong><br>
                        Für eine aussagekräftige Korrelationsanalyse werden mindestens 3 Datenpunkte benötigt.
                    </p>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px;">
                        <div style="background: white; padding: 15px; border-radius: 8px;">
                            <div style="font-size: 0.9em; color: #6c757d; margin-bottom: 5px;">Datenpunkte</div>
                            <div style="font-size: 1.8em; font-weight: bold; color: #856404;">{n}</div>
                            <div style="font-size: 0.85em; color: #856404; margin-top: 5px;">Zu wenig</div>
                        </div>
                        <div style="background: white; padding: 15px; border-radius: 8px;">
                            <div style="font-size: 0.9em; color: #6c757d; margin-bottom: 5px;">Ø Sentiment</div>
                            <div style="font-size: 1.8em; font-weight: bold; color: #495057;">{avg_sent:+.3f}</div>
                        </div>
                    </div>
                    <p style="color: #856404; margin-top: 15px; font-size: 0.9em;">
                        💡 <em>Tipp: Erhöhe den Zeitraum oder warte auf mehr Nachrichten zu diesem Ticker.</em>
                    </p>
                </div>
                """
            else:
                # Normale Anzeige mit ausreichend Daten
                significance = "✅ Signifikant" if p_val < 0.05 else "⚠️ Nicht signifikant"
                
                if abs(corr) < 0.1:
                    strength = "Keine"
                elif abs(corr) < 0.3:
                    strength = "Schwache"
                elif abs(corr) < 0.5:
                    strength = "Moderate"
                else:
                    strength = "Starke"
                
                stats_html = f"""
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 30px;">
                        <h3 style="color: #667eea; margin-bottom: 15px;">📊 Statistik für {ticker}</h3>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                            <div style="background: white; padding: 15px; border-radius: 8px; border-left: 4px solid #667eea;">
                                <div style="font-size: 0.9em; color: #6c757d; margin-bottom: 5px;">Korrelation</div>
                                <div style="font-size: 1.8em; font-weight: bold; color: #667eea;">{corr:.4f}</div>
                                <div style="font-size: 0.85em; color: #6c757d; margin-top: 5px;">{strength}</div>
                            </div>
                            <div style="background: white; padding: 15px; border-radius: 8px; border-left: 4px solid #28a745;">
                                <div style="font-size: 0.9em; color: #6c757d; margin-bottom: 5px;">Signifikanz</div>
                                <div style="font-size: 1.2em; font-weight: bold; color: #495057; margin-top: 10px;">{significance}</div>
                                <div style="font-size: 0.85em; color: #6c757d; margin-top: 5px;">p = {p_val:.4f}</div>
                            </div>
                            <div style="background: white; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107;">
                                <div style="font-size: 0.9em; color: #6c757d; margin-bottom: 5px;">Datenpunkte</div>
                                <div style="font-size: 1.8em; font-weight: bold; color: #495057;">{n}</div>
                            </div>
                            <div style="background: white; padding: 15px; border-radius: 8px; border-left: 4px solid #17a2b8;">
                                <div style="font-size: 0.9em; color: #6c757d; margin-bottom: 5px;">Ø Sentiment</div>
                                <div style="font-size: 1.8em; font-weight: bold; color: #495057;">{avg_sent:+.3f}</div>
                            </div>
                        </div>
                    </div>
                """
        
        html_content += f"""
            <!-- {ticker} Sektion -->
            <div id="{ticker}" class="ticker-section">
                <h2 class="ticker-title">{ticker}</h2>
                
                {stats_html}
                
                <div class="plot-container">
                    <div class="plot-label">📊 Sentiment vs. Volatilität (Zeitreihe)</div>
                    <iframe src="{ticker}_sentiment_volatility.html"></iframe>
                </div>
                
                <div class="plot-container">
                    <div class="plot-label">📈 Korrelations-Scatterplot</div>
                    <iframe src="{ticker}_correlation.html"></iframe>
                </div>
            </div>
"""
    
    html_content += """
        </div>
        
        <div class="footer">
            <p>🎓 Universität Projekt | Applied Finance in Python | Dezember 2025</p>
            <p style="margin-top: 10px;">Sentiment-Analyse mit FinBERT | Daten: Yahoo Finance | Visualisierung: Plotly</p>
        </div>
    </div>
    
    <script>
        function showSection(sectionId) {
            // Alle Sektionen ausblenden
            document.querySelectorAll('.ticker-section, .overview-section').forEach(section => {
                section.classList.remove('active');
            });
            
            // Alle Buttons deaktivieren
            document.querySelectorAll('.nav-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Ausgewählte Sektion anzeigen
            document.getElementById(sectionId).classList.add('active');
            
            // Entsprechenden Button aktivieren
            event.target.classList.add('active');
        }
    </script>
</body>
</html>
"""
    
    return html_content


def save_dashboard(tickers, ticker_stats=None, output_dir='plots'):
    """Erstellt und speichert das Dashboard."""
    html = create_dashboard(tickers, ticker_stats)
    
    filepath = os.path.join(output_dir, 'index.html')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return filepath
