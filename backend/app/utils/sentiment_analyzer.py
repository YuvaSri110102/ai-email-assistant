from transformers import pipeline

# Load once at startup
sentiment_pipeline = pipeline("sentiment-analysis")

def analyze_sentiment(text: str):
    if not text or text.strip() == "":
        return None, None

    result = sentiment_pipeline(text[:512])[0]
    label = result["label"].lower()
    score = float(result["score"])
    return label, score
