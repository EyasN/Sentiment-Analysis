# Sentiment-Strategie und Modell-Dokumentation

## 1. Definition von Sentiment im finanzwirtschaftlichen Kontext

In diesem Projekt definieren wir "Sentiment" nicht als allgemeine emotionale Stimmung (glücklich/traurig), sondern spezifisch als **Marktstimmung**:

- **Positiv (+1):** Nachrichten, die auf steigende Kurse, Gewinne, Wachstum oder positive Marktbedingungen hindeuten.
- **Negativ (-1):** Nachrichten über Verluste, Risiken, Klagen, Rezession oder negative Marktauswirkungen.
- **Neutral (0):** Reine Faktenberichte ohne Wertung (z.B. "Hauptversammlung findet am Dienstag statt").

## 2. Modellwahl: FinBERT statt generatives LLM

Für die Analyse wurde **FinBERT** (`ProsusAI/finbert`) gewählt.

**Begründung:**
- FinBERT ist ein BERT-Modell, das spezifisch auf einem riesigen Korpus von Finanztexten (TRC2-financial) nachtrainiert wurde.
- Es übertrifft generische LLMs (wie GPT-3.5 ohne Few-Shot-Prompting) oft in der Klassifikation von Finanzsprache, da es Nuancen wie "Verlust verringert" (positiv!) korrekt versteht, wo Standard-Modelle oft "Verlust" als negativ werten.

## 3. Berechnung des Sentiment-Scores

Das Modell gibt für jeden Text Wahrscheinlichkeiten für drei Klassen aus:
$P_{pos}, P_{neg}, P_{neu}$ (wobei $P_{pos} + P_{neg} + P_{neu} = 1$).

Der quantitative Score wird wie folgt berechnet:

$$ Score = P_{pos} - P_{neg} $$

**Eigenschaften dieser Metrik:**
- **Wertebereich:** $[-1, +1]$
- **Umgang mit Neutralität:** Ein rein neutraler Text ($P_{neu} \approx 1, P_{pos} \approx 0, P_{neg} \approx 0$) ergibt einen Score von 0.
- **Umgang mit Widersprüchen:** Wenn ein Text sowohl positive als auch negative Aspekte enthält (z.B. $P_{pos}=0.4, P_{neg}=0.3$), heben sie sich teilweise auf, was zu einem leicht positiven Score von $0.1$ führt. Dies spiegelt die Unsicherheit im Markt wider.

## 4. Aggregation

Da Volatilität ein Tageswert ist, müssen die Sentiment-Scores der einzelnen Nachrichten aggregiert werden:

$$ Sentiment_{Tag} = \frac{1}{N} \sum_{i=1}^{N} Score_i $$

Dies repräsentiert die "durchschnittliche Marktstimmung" des Tages.
