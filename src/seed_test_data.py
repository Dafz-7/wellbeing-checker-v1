from datetime import datetime, timedelta
import sqlite3, random

DB_NAME = "wellbeing.db"

LEVELS = ["very sad", "sad", "normal", "happy", "very happy"]
EXAMPLE_TEXT = {
    "very sad": "I feel miserable and hopeless.",
    "sad": "I am tired and lonely.",
    "normal": "It was an okay day.",
    "happy": "I feel happy and grateful.",
    "very happy": "Today was amazing and wonderful!"
}
POLARITY = {"very sad": -0.8, "sad": -0.4, "normal": 0.0, "happy": 0.5, "very happy": 0.9}

def seed(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Start from Sept 1, 2025
    start = datetime(2025, 9, 1)
    end = datetime(2025, 12, 13)  # up to yesterday

    days = (end - start).days + 1
    for i in range(days):
        d = start + timedelta(days=i)
        level = random.choice(LEVELS)
        entry = EXAMPLE_TEXT[level]
        pol = POLARITY[level]
        ts = d.strftime("%Y-%m-%d %I:%M:%S %p")
        c.execute("""
            INSERT INTO diary (user_id, entry, timestamp, wellbeing_level, polarity)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, entry, ts, level, pol))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    seed(user_id=1)
