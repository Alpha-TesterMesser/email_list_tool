import sqlite3
from db import get_db

conn = get_db()
# Add new columns one at a time; sqlite3 allows only one statement per execute
for stmt in (
    "ALTER TABLE subscribers ADD COLUMN verified INTEGER DEFAULT 0",
    "ALTER TABLE subscribers ADD COLUMN verification_code TEXT",
    "ALTER TABLE subscribers ADD COLUMN code_expires_at TEXT",
):
    try:
        conn.execute(stmt)
    except sqlite3.OperationalError:
        # Column likely already exists; ignore
        pass

conn.commit()
conn.close()