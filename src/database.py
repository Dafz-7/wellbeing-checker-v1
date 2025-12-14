import sqlite3
from datetime import datetime

DB_NAME = "wellbeing.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    # Diary entries table (with wellbeing_level column)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS diary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        entry TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        wellbeing_level TEXT,
        polarity REAL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # Settings table (only timer_length now)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        user_id INTEGER PRIMARY KEY,
        timer_length INTEGER DEFAULT 1800,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # Monthly summary table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS monthly_summary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        year INTEGER NOT NULL,
        month INTEGER NOT NULL,
        very_sad_count INTEGER DEFAULT 0,
        sad_count INTEGER DEFAULT 0,
        normal_count INTEGER DEFAULT 0,
        happy_count INTEGER DEFAULT 0,
        very_happy_count INTEGER DEFAULT 0,
        avg_polarity REAL DEFAULT 0,
        happiest_day TEXT,
        happiest_entry TEXT,
        generated_at TEXT NOT NULL,
        UNIQUE(user_id, year, month),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()

# ---------------- User Management ----------------

def add_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        user_id = cursor.lastrowid

        # Insert default settings row for this user
        cursor.execute("INSERT INTO settings (user_id, timer_length) VALUES (?, 1800)", (user_id,))

        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def check_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def ensure_settings(user_id):
    """Guarantee that a settings row exists for this user (for older accounts)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM settings WHERE user_id=?", (user_id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO settings (user_id, timer_length) VALUES (?, 1800)", (user_id,))
        conn.commit()
    conn.close()

def get_user_id(username):
    """Return the user_id for a given username, or None if not found."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# ---------------- Diary Management ----------------

def add_entry(user_id, entry, timestamp):
    """Add diary entry without sentiment (legacy)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO diary (user_id, entry, timestamp) VALUES (?, ?, ?)",
                   (user_id, entry, timestamp))
    conn.commit()
    conn.close()

def add_entry_with_sentiment(user_id, entry, timestamp, wellbeing_level, polarity):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO diary (user_id, entry, timestamp, wellbeing_level, polarity)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, entry, timestamp, wellbeing_level, polarity))
    conn.commit()
    conn.close()

def get_entries(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT entry, timestamp, wellbeing_level, polarity FROM diary WHERE user_id=? ORDER BY timestamp DESC",
                   (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# ---------------- Settings Management ----------------

def update_user_settings(user_id, timer_length=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if timer_length is not None:
        cursor.execute("UPDATE settings SET timer_length=? WHERE user_id=?", (timer_length, user_id))
    conn.commit()
    conn.close()

def get_user_settings(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT timer_length FROM settings WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"timer_length": row[0]}
    return None

# ---------------- Monthly Summary Helpers ----------------

def get_entries_for_month(user_id, year, month):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        SELECT entry, timestamp, wellbeing_level, polarity
        FROM diary
        WHERE user_id = ?
          AND substr(timestamp, 1, 7) = ?
        ORDER BY timestamp ASC
    """, (user_id, f"{year}-{month:02d}"))
    rows = c.fetchall()
    conn.close()
    return rows

def compute_month_stats(rows):
    counts = {"very sad": 0, "sad": 0, "normal": 0, "happy": 0, "very happy": 0}
    polarities = []
    happiest = {"polarity": -2, "timestamp": None, "entry": None}
    for entry, ts, level, pol in rows:
        if level in counts:
            counts[level] += 1
        if pol is not None:
            polarities.append(pol)
            if pol > happiest["polarity"]:
                happiest = {"polarity": pol, "timestamp": ts, "entry": entry}
    avg_pol = sum(polarities) / len(polarities) if polarities else 0.0
    return {
        "counts": counts,
        "avg_polarity": avg_pol,
        "happiest_day": happiest["timestamp"],
        "happiest_entry": happiest["entry"]
    }

def upsert_monthly_summary(user_id, year, month, stats):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO monthly_summary (
            user_id, year, month,
            very_sad_count, sad_count, normal_count, happy_count, very_happy_count,
            avg_polarity, happiest_day, happiest_entry, generated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id, year, month) DO UPDATE SET
            very_sad_count=excluded.very_sad_count,
            sad_count=excluded.sad_count,
            normal_count=excluded.normal_count,
            happy_count=excluded.happy_count,
            very_happy_count=excluded.very_happy_count,
            avg_polarity=excluded.avg_polarity,
            happiest_day=excluded.happiest_day,
            happiest_entry=excluded.happiest_entry,
            generated_at=excluded.generated_at
    """, (
        user_id, year, month,
        stats["counts"]["very sad"], stats["counts"]["sad"], stats["counts"]["normal"],
        stats["counts"]["happy"], stats["counts"]["very happy"],
        stats["avg_polarity"], stats["happiest_day"], stats["happiest_entry"],
        datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    ))
    conn.commit()
    conn.close()

def get_monthly_summary(user_id, year, month):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        SELECT very_sad_count, sad_count, normal_count, happy_count, very_happy_count,
               avg_polarity, happiest_day, happiest_entry, generated_at
        FROM monthly_summary
        WHERE user_id = ? AND year = ? AND month = ?
    """, (user_id, year, month))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "counts": {
            "very sad": row[0], "sad": row[1], "normal": row[2],
            "happy": row[3], "very happy": row[4]
        },
        "avg_polarity": row[5],
        "happiest_day": row[6],
        "happiest_entry": row[7],
        "generated_at": row[8]
    }

def list_all_monthly_summaries(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        SELECT year, month, very_sad_count, sad_count, normal_count, happy_count, very_happy_count,
               avg_polarity, happiest_day, generated_at
        FROM monthly_summary
        WHERE user_id = ?
        ORDER BY year DESC, month DESC
    """, (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows
