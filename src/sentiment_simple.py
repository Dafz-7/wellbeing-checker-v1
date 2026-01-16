"""
Sentiment Analysis Helper for the app.
Uses TextBlob to analyze sentiment polarity of diary entries and maps results
to wellbeing levels (very sad → very happy).
"""

from textblob import TextBlob


def analyze_sentiment(text: str):
    """
    Analyze sentiment of given text using TextBlob.
    Parameters:
        text (str): The diary entry text
    Returns:
        tuple (wellbeing_level, polarity)
            - wellbeing_level (str): Categorized wellbeing level based on polarity
            - polarity (float): Sentiment polarity score (-1.0 = very negative, +1.0 = very positive)

    Mapping rules:
        polarity <= -0.6   → "very sad"
        -0.6 < polarity < -0.2 → "sad"
        -0.2 <= polarity <= 0.2 → "normal"
        0.2 < polarity < 0.6 → "happy"
        polarity >= 0.6   → "very happy"
    """
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