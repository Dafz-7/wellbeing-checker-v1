from textblob import TextBlob

def analyze_sentiment(text: str):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity

    # Map polarity to wellbeing level
    if polarity <= -0.6:
        wellbeing_level = "very sad"
    elif polarity < -0.2:
        wellbeing_level = "sad"
    elif polarity <= 0.2:
        wellbeing_level = "normal"
    elif polarity < 0.6:
        wellbeing_level = "happy"
    else:
        wellbeing_level = "very happy"

    return wellbeing_level, polarity
