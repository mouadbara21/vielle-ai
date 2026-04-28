from textblob import TextBlob
from textblob_fr import PatternTagger, PatternAnalyzer

def analyze_sentiment(text: str) -> float:
    """Analyze sentiment of text. Returns value between -1.0 (negative) and 1.0 (positive).
    Using textblob_fr for simplicity and speed.
    """
    if not text:
        return 0.0
    
    blob = TextBlob(text, pos_tagger=PatternTagger(), analyzer=PatternAnalyzer())
    # Sentiment is a tuple (polarity, subjectivity)
    # Polarity is between -1.0 and 1.0
    return blob.sentiment[0]
