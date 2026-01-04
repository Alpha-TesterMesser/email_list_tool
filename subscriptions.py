import csv
import os

CSV_PATH = os.path.abspath("emails.csv")


def ensure_csv_has_header():
    """Ensure the CSV exists and has a 'send' column. Migrate old two-column files by adding 'Yes'."""
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["time", "email", "send"])
        return

    # Read existing content
    with open(CSV_PATH, "r", encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))

    if not rows:
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["time", "email", "send"])
        return

    header = rows[0]
    # If header already contains send and looks correct, nothing to do
    if "send" in header and header[0:2] == ["time", "email"]:
        return

    # Determine data rows (if first row is header or not)
    if header == ["time", "email"] or header == ["time", "email", "send"]:
        data_rows = rows[1:]
    else:
        data_rows = rows

    new_rows = [["time", "email", "send"]]
    for r in data_rows:
        if len(r) >= 2:
            t = r[0]
            e = r[1]
            s = r[2] if len(r) > 2 else "Yes"
            new_rows.append([t, e, s])

    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(new_rows)


def append_subscription(time, email, send=True):
    ensure_csv_has_header()
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([time, email, "Yes" if send else "No"])


def update_send_in_csv(email, send):
    """Update all rows with matching email to set send to Yes/No."""
    if not os.path.exists(CSV_PATH):
        return
    with open(CSV_PATH, "r", encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    if not rows:
        return
    header = rows[0]
    if "send" not in header:
        ensure_csv_has_header()
        with open(CSV_PATH, "r", encoding="utf-8", newline="") as f:
            rows = list(csv.reader(f))
        header = rows[0]

    updated = False
    for i, row in enumerate(rows[1:], start=1):
        if len(row) >= 2 and row[1].strip().lower() == email.strip().lower():
            # Ensure row has at least 3 columns
            while len(row) < 3:
                row.append("Yes")
            row[2] = "Yes" if send else "No"
            rows[i] = row
            updated = True

    if updated:
        with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)