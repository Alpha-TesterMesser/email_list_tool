import logging
import sqlite3
import os

log = logging.getLogger(__name__)
DB_PATH = os.path.abspath("emails.db")


def get_db():
    # Use absolute path and a longer timeout to reduce 'database is locked' errors.
    conn = sqlite3.connect(DB_PATH, timeout=30, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    try:
        # attempt to enable WAL for better concurrency; ignore if not supported
        conn.execute("PRAGMA journal_mode=WAL;")
    except sqlite3.DatabaseError:
        pass
    return conn


def init_db():
    """Create the table if missing, keep 'time', and ensure the 'send' boolean (INTEGER) column exists.

    If an older DB has an 'active' column, migrate its values into 'send'.
    """
    conn = None
    try:
        conn = get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS subscribers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                time TEXT,
                send INTEGER DEFAULT 1
            )
        """)
        # Inspect columns and add/repair as needed
        cur = conn.execute("PRAGMA table_info(subscribers);")
        cols = [row[1] for row in cur.fetchall()]
        if "time" not in cols:
            conn.execute("ALTER TABLE subscribers ADD COLUMN time TEXT")
        if "send" not in cols:
            # If an old 'active' column exists, add 'send' and populate from it
            conn.execute("ALTER TABLE subscribers ADD COLUMN send INTEGER DEFAULT 1")
            if "active" in cols:
                conn.execute("UPDATE subscribers SET send = active WHERE active IS NOT NULL")
            conn.execute("UPDATE subscribers SET send = 1 WHERE send IS NULL")

        # Ensure verification-related columns exist for signup/verify flow
        if "verified" not in cols:
            conn.execute("ALTER TABLE subscribers ADD COLUMN verified INTEGER DEFAULT 0")
            conn.execute("UPDATE subscribers SET verified = 0 WHERE verified IS NULL")
        if "verification_code" not in cols:
            conn.execute("ALTER TABLE subscribers ADD COLUMN verification_code TEXT")
        if "code_expires_at" not in cols:
            conn.execute("ALTER TABLE subscribers ADD COLUMN code_expires_at TEXT")

        # If send exists but active exists too, leave active untouched but prefer 'send'
        conn.commit()
    except Exception as e:
        # Log the error so failures to initialize don't remain silent
        log.exception("Failed to initialize the database: %s", e)
        raise
    finally:
        if conn:
            conn.close()