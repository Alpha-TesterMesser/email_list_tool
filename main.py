import tkinter as tk
from tkinter import ttk
from db import get_db
import sqlite3

REFRESH_INTERVAL_SECONDS = 5

def fetch_rows():
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        # Include verification-related columns so the GUI can display code/status/expiry
        cursor.execute("SELECT id, email, time, send, verified, verification_code, code_expires_at FROM subscribers ORDER BY id")
        return cursor.fetchall()
    except sqlite3.OperationalError as e:
        print("Database error:", e)
        return []
    finally:
        if conn:
            conn.close()


# How often to auto-refresh (seconds). Change this variable to adjust behavior.

rows = fetch_rows()

window = tk.Tk()
window.title("Subscribers")
window.geometry("900x420")

# Top frame for controls
controls = ttk.Frame(window)
controls.pack(fill="x", padx=10, pady=(10, 0))

refresh_btn = ttk.Button(controls, text="Refresh")
refresh_btn.pack(side="left")

interval_label = ttk.Label(controls, text=f"Auto-refresh every {REFRESH_INTERVAL_SECONDS}s")
interval_label.pack(side="left", padx=(8, 0))

frame = ttk.Frame(window)
frame.pack(fill="both", expand=True, padx=10, pady=10)

columns = ("id", "email", "time", "send", "verified", "verification_code", "code_expires_at")
tree = ttk.Treeview(frame, columns=columns, show="headings")
tree.heading("id", text="ID")
tree.heading("email", text="Email")
tree.heading("time", text="Time")
tree.heading("send", text="Send")
tree.heading("verified", text="Verified?")
tree.heading("verification_code", text="V. Code")
tree.heading("code_expires_at", text="Code Expires")
tree.column("id", width=60, anchor="center")
tree.column("email", width=200, anchor="w")
tree.column("time", width=140, anchor="center")
tree.column("send", width=80, anchor="center")
tree.column("verified", width=80, anchor="center")
tree.column("verification_code", width=120, anchor="center")
tree.column("code_expires_at", width=120, anchor="center")

vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=vsb.set)
tree.grid(row=0, column=0, sticky="nsew")
vsb.grid(row=0, column=1, sticky="ns")

frame.rowconfigure(0, weight=1)
frame.columnconfigure(0, weight=1)

from datetime import datetime

# Keep track of the scheduled auto-refresh job so we can cancel it on exit
_refresh_job_id = None


def populate_tree(rows):
    # Clear existing rows
    for item in tree.get_children():
        tree.delete(item)

    if not rows:
        tree.insert("", "end", values=("", "No subscribers yet.", "", "", "", "", ""))
        return

    for r in rows:
        send_display = "Yes" if r["send"] in (1, "1", True) else "No"
        verified_display = "Yes" if r["verified"] in (1, "1", True) else "No"
        time_display = r["time"] or ""

        # verification_code stored is a hash; show a short/truncated fingerprint for inspection
        code_raw = r["verification_code"]
        if code_raw:
            code_display = (code_raw[:8] + "...") if len(code_raw) > 8 else code_raw
        else:
            code_display = ""

        # compute time until expiry in minutes/seconds
        expires_raw = r["code_expires_at"]
        if expires_raw:
            try:
                expires_dt = datetime.fromisoformat(expires_raw)
                now = datetime.utcnow()
                delta = expires_dt - now
                secs = int(delta.total_seconds())
                if secs <= 0:
                    expires_display = "Expired"
                else:
                    mins = secs // 60
                    rem = secs % 60
                    expires_display = f"{mins}m {rem}s"
            except Exception:
                expires_display = expires_raw
        else:
            expires_display = ""

        tree.insert("", "end", values=(r["id"], r["email"], time_display, send_display, verified_display, code_display, expires_display))


def refresh_rows():
    """Fetch rows and populate the tree. This function also schedules the next auto-refresh."""
    global _refresh_job_id
    rows = fetch_rows()
    populate_tree(rows)

    # Schedule next refresh
    try:
        _refresh_job_id = window.after(REFRESH_INTERVAL_SECONDS * 1000, refresh_rows)
    except Exception:
        _refresh_job_id = None


# Bind the refresh button to an immediate refresh
refresh_btn.configure(command=refresh_rows)


# Cancel scheduled job and exit cleanly
def on_close():
    global _refresh_job_id
    if _refresh_job_id is not None:
        try:
            window.after_cancel(_refresh_job_id)
        except Exception:
            pass
    window.destroy()

window.protocol("WM_DELETE_WINDOW", on_close)

# Start initial population and auto-refresh
refresh_rows()

window.mainloop()