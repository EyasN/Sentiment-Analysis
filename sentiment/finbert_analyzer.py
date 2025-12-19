from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import pandas as pd


# FinBERT Modell und Tokenizer
MODEL_NAME = "ProsusAI/finbert"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

def analyze_sentiment(text):
    """Analysiert Sentiment eines Textes mit FinBERT."""
    # 1. Text tokenisieren
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    
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


def analyze_dataframe(df, text_column='title'):
    """Analysiert Sentiment für alle Texte in einem DataFrame."""
    print(f"Analysiere {len(df)} Texte mit FinBERT...")
    
    scores = []
    for i, text in enumerate(df[text_column]):
        if i % 10 == 0:
            print(f"  Fortschritt: {i}/{len(df)}")
        
        try:
            score = analyze_sentiment(text)
        except Exception as e:
            print(f"  Fehler bei Text {i}: {e}")
            score = 0.0  # Neutral bei Fehler
        
        scores.append(score)
    
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