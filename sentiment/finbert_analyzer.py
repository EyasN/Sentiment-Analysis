from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import pandas as pd


# FinBERT Modell und Tokenizer
MODEL_NAME = "ProsusAI/finbert"

# GPU-Unterstützung prüfen
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"FinBERT läuft auf: {device}")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
model.to(device)  # Modell auf GPU verschieben (falls verfügbar)

def analyze_sentiment(text):
    """Analysiert Sentiment eines Textes mit FinBERT."""
    # 1. Text tokenisieren
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    inputs = {key: val.to(device) for key, val in inputs.items()}  # Auf GPU verschieben
    
    # 2. Durch Modell schicken
    with torch.no_grad():
        outputs = model(**inputs)
    
    # 3. Softmax für Wahrscheinlichkeiten
    probs = torch.softmax(outputs.logits, dim=1)
    
    # 4. FinBERT: [negative, neutral, positive]
    negative, neutral, positive = probs[0].tolist()
    
    # 5. Score berechnen: -1 bis +1
    score = positive - negative
    
    return score


def analyze_dataframe(df, text_column='title', batch_size=16):
    """
    Analysiert Sentiment für alle Texte in einem DataFrame.
    
    Args:
        df: DataFrame mit Texten
        text_column: Spalte mit den Texten
        batch_size: Anzahl Texte pro Batch (Standard: 16)
    """
    print(f"Analysiere {len(df)} Texte mit FinBERT (Batch-Size: {batch_size})...")
    
    scores = []
    texts = df[text_column].tolist()
    
    # Batch-Processing für bessere Performance
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        print(f"  Fortschritt: {i}/{len(texts)}")
        
        try:
            # Batch tokenisieren
            inputs = tokenizer(batch_texts, return_tensors="pt", truncation=True, 
                             max_length=512, padding=True)
            inputs = {key: val.to(device) for key, val in inputs.items()}
            
            # Batch durch Modell
            with torch.no_grad():
                outputs = model(**inputs)
            
            probs = torch.softmax(outputs.logits, dim=1)
            
            # Scores für alle Texte im Batch berechnen
            for prob in probs:
                negative, neutral, positive = prob.tolist()
                score = positive - negative
                scores.append(score)
                
        except Exception as e:
            print(f"  Fehler bei Batch {i}: {e}")
            # Bei Fehler: Neutral-Score für alle Texte im Batch
            scores.extend([0.0] * len(batch_texts))
    
    df = df.copy()
    df['sentiment_score'] = scores
    print("Fertig!")
    
    return df


def aggregate_daily_sentiment(df):
    """Aggregiert Sentiment pro Tag und Ticker."""
    df['date'] = pd.to_datetime(df['date'])
    
    daily = df.groupby(['ticker', 'date']).agg({
        'sentiment_score': 'mean',  # Durchschnitt pro Tag
        'title': 'count'  # Anzahl Artikel
    }).reset_index()
    
    daily.columns = ['ticker', 'date', 'sentiment_score', 'news_count']
    
    return daily


def aggregate_weekly_sentiment(df):
    """Aggregiert Sentiment pro Woche und Ticker."""
    df['date'] = pd.to_datetime(df['date'])
    
    # Woche des Jahres berechnen (ISO Woche)
    df['year_week'] = df['date'].dt.strftime('%Y-W%U')
    
    weekly = df.groupby(['ticker', 'year_week']).agg({
        'sentiment_score': 'mean',  # Durchschnitt pro Woche
        'title': 'count',  # Anzahl Artikel
        'date': 'min'  # Erster Tag der Woche für Zuordnung
    }).reset_index()
    
    weekly.columns = ['ticker', 'year_week', 'sentiment_score', 'news_count', 'date']
    
    return weekly


# Test
if __name__ == "__main__":
    # Einzelne Texte testen
    test_texts = [
        "Apple reports record quarterly revenue and profit",
        "Stock market crashes amid recession fears",
        "Company announces regular quarterly dividend"
    ]
    
    print("=== FinBERT Sentiment Test ===\n")
    
    for text in test_texts:
        score = analyze_sentiment(text)
        print(f"Text: {text}")
        print(f"Score: {score:.3f}")
        print()