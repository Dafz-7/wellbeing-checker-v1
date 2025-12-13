import sqlite3

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

    # Diary entries table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS diary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        entry TEXT NOT NULL,
        timestamp TEXT NOT NULL,
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

    conn.commit()
    conn.close()

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

def add_entry(user_id, entry, timestamp):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO diary (user_id, entry, timestamp) VALUES (?, ?, ?)", (user_id, entry, timestamp))
    conn.commit()
    conn.close()

def get_entries(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT entry, timestamp FROM diary WHERE user_id=? ORDER BY timestamp DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

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
