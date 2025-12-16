import sqlite3
from datetime import datetime, timedelta
from textblob import TextBlob

DB_NAME = "wellbeing.db"

# Sentiment analyzer copied from sentiment_simple.py
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

# Example seed entries (customize these as you like)
SEED_ENTRIES = [
    "I am tired and lonely.",
    "Today was amazing and wonderful!",
    "It was an okay day.",
    "I feel miserable and hopeless.",
    "I feel happy and grateful.",
    "I feel happy today!"
]

def reset_and_seed_diary(user_id=1):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. Delete all existing diary entries
    cursor.execute("DELETE FROM diary")

    # 2. Seed new entries from August 1, 2025 to December 15, 2025
    start_date = datetime(2025, 8, 1)
    end_date = datetime(2025, 12, 15)
    delta = timedelta(days=1)

    current = start_date
    while current <= end_date:
        # Pick a sample entry cyclically
        entry_text = SEED_ENTRIES[(current.day % len(SEED_ENTRIES))]

        # Use your sentiment analyzer
        wellbeing_level, polarity = analyze_sentiment(entry_text)

        # Original timestamp format (12-hour clock with AM/PM)
        timestamp = current.strftime("%Y-%m-%d %I:%M:%S %p")
        date_str = current.strftime("%Y-%m-%d")

        cursor.execute("""
            INSERT INTO diary (user_id, entry, timestamp, date, wellbeing_level, polarity)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, entry_text, timestamp, date_str, wellbeing_level, polarity))

        current += delta

    conn.commit()
    conn.close()
    print("✅ Diary reset and reseeded from Aug 1 to Dec 15, 2025.")

if __name__ == "__main__":
    reset_and_seed_diary(user_id=1)