from transformers import pipeline

sentiment_pipeline = pipeline("sentiment-analysis")

def analyze_sentiment(text: str) -> str:
    if not text or text.strip() == "":
        return "neutral"
    
    result = sentiment_pipeline(text[:512])[0]
    label = result["label"].lower()

    if "pos" in label:
        return "positive"
    elif "neg" in label:
        return "negative"
    else:
        return "neutral"