"""
Database module for the app.
Handles initialization of SQLite database and schema migrations.
Tables:
- users: stores user credentials
- diary: stores daily diary entries with sentiment analysis
- settings: stores user-specific app settings (e.g., timer length)
- monthly_summary: stores aggregated monthly wellbeing statistics
"""

import sqlite3
from datetime import datetime

DB_NAME = "wellbeing.db"


def init_db():
    """
    Initialize the SQLite database:
    - Create tables if they do not exist (users, diary, settings, monthly_summary)
    - Run migration to enforce uniqueness in diary entries (one per user per day)
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # ---------------- Users table ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    # ---------------- Diary entries table ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS diary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        entry TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        date TEXT,
        wellbeing_level TEXT,
        polarity REAL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # ---------------- Settings table ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        user_id INTEGER PRIMARY KEY,
        timer_length INTEGER DEFAULT 1800,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # ---------------- Monthly summary table ----------------
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

    # Run migration to enforce uniqueness in diary entries
    _migrate_diary_date_and_uniqueness(cursor)

    conn.commit()
    conn.close()


def _migrate_diary_date_and_uniqueness(cursor):
    """
    Migration helper for diary table:
    - Ensure 'date' column exists
    - Backfill 'date' values from 'timestamp'
    - Remove duplicate entries (keep earliest entry per user/date)
    - Create unique index on (user_id, date)
    """
    # Ensure 'date' column exists
    cursor.execute("PRAGMA table_info(diary)")
    cols = [row[1] for row in cursor.fetchall()]
    if "date" not in cols:
        cursor.execute("ALTER TABLE diary ADD COLUMN date TEXT")

    # Backfill 'date' values from 'timestamp'
    cursor.execute("UPDATE diary SET date = substr(timestamp, 1, 10) WHERE date IS NULL OR date = ''")

    # Remove duplicates (keep earliest id per user/date)
    cursor.execute("""
        DELETE FROM diary
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM diary
            GROUP BY user_id, date
        )
    """)

    # Create unique index on (user_id, date)
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_diary_user_date
        ON diary(user_id, date)
    """)


# ---------------- User Management ----------------

def add_user(username, password):
    """
    Add a new user to the database.
    - Inserts username and password into 'users' table.
    - Automatically creates a default settings row (timer_length = 1800 seconds).
    Returns:
        True if user successfully added,
        False if username already exists (IntegrityError).
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        user_id = cursor.lastrowid
        cursor.execute("INSERT INTO settings (user_id, timer_length) VALUES (?, 1800)", (user_id,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def check_user(username, password):
    """
    Check if a user exists with given username and password.
    Returns:
        user_id if credentials are valid,
        None otherwise.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def ensure_settings(user_id):
    """
    Ensure that a settings row exists for the given user_id.
    - If no settings exist, insert a default row (timer_length = 1800).
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM settings WHERE user_id=?", (user_id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO settings (user_id, timer_length) VALUES (?, 1800)", (user_id,))
        conn.commit()
    conn.close()


def get_user_id(username):
    """
    Fetch user_id for a given username.
    Returns:
        user_id if found,
        None otherwise.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


# ---------------- Diary Management ----------------

def add_entry(user_id, entry, timestamp):
    """
    Add a diary entry for a user.
    - Extracts date from timestamp.
    - Inserts entry into 'diary' table.
    Returns:
        True if entry successfully added,
        False if duplicate entry exists for same user/date.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    date_str = _extract_date(timestamp)
    try:
        cursor.execute("INSERT INTO diary (user_id, entry, timestamp, date) VALUES (?, ?, ?, ?)",
                       (user_id, entry, timestamp, date_str))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def add_entry_with_sentiment(user_id, entry, timestamp, wellbeing_level, polarity):
    """
    Add a diary entry with sentiment analysis results.
    - Extracts date from timestamp.
    - Inserts entry, wellbeing_level, and polarity into 'diary' table.
    Returns:
        True if entry successfully added,
        False if duplicate entry exists for same user/date.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    date_str = _extract_date(timestamp)
    try:
        cursor.execute("""
            INSERT INTO diary (user_id, entry, timestamp, date, wellbeing_level, polarity)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, entry, timestamp, date_str, wellbeing_level, polarity))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_entries(user_id):
    """
    Fetch all diary entries for a given user.
    - Returns entry text, timestamp, wellbeing_level, and polarity.
    - Ordered by timestamp (latest first).
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT entry, timestamp, wellbeing_level, polarity
        FROM diary
        WHERE user_id=?
        ORDER BY timestamp DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


# ---------------- Settings Management ----------------

def update_user_settings(user_id, timer_length=None):
    """
    Update user settings in the database.
    Parameters:
        user_id (int): ID of the user
        timer_length (int, optional): New session timer length in seconds
    - If timer_length is provided, update the settings row for the user.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if timer_length is not None:
        cursor.execute("UPDATE settings SET timer_length=? WHERE user_id=?", (timer_length, user_id))
    conn.commit()
    conn.close()


def get_user_settings(user_id):
    """
    Fetch user settings from the database.
    Parameters:
        user_id (int): ID of the user
    Returns:
        dict with 'timer_length' if settings exist,
        None otherwise.
    """
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
    """
    Fetch all diary entries for a given user and month.
    Parameters:
        user_id (int): ID of the user
        year (int): Year of entries
        month (int): Month of entries
    Returns:
        List of tuples (entry, timestamp, wellbeing_level, polarity).
    """
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
    """
    Compute statistics for a given month's diary entries.
    Parameters:
        rows (list): List of diary entries with sentiment data
    Returns:
        dict containing:
            - counts: distribution of wellbeing levels
            - avg_polarity: average sentiment polarity
            - happiest_day: timestamp of happiest entry
            - happiest_entry: text of happiest entry
    """
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
    """
    Insert or update monthly summary for a user.
    Parameters:
        user_id (int): ID of the user
        year (int): Year of summary
        month (int): Month of summary
        stats (dict): Computed statistics for the month
    - Uses SQLite UPSERT to update if summary already exists.
    """
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
    """
    Fetch monthly summary for a given user, year, and month.
    Returns:
        dict containing counts, avg_polarity, happiest_day, happiest_entry, generated_at
        or None if no summary exists.
    """
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
    """
    List all monthly summaries for a given user.
    Returns:
        List of tuples (year, month, counts, avg_polarity, happiest_day, generated_at).
        Ordered by year and month descending.
    """
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


# ---------------- Utils ----------------

def _extract_date(timestamp_str):
    """
    Utility function to extract date from timestamp string.
    Parameters:
        timestamp_str (str): Timestamp in format 'YYYY-MM-DD HH:MM:SS' or ISO format
    Returns:
        str: First 10 characters (date segment, 'YYYY-MM-DD')
    """
    # Expecting formats like 'YYYY-MM-DD HH:MM:SS' or ISO timestamps;
    # first 10 chars should be the date segment.
    return timestamp_str[:10]