import re
import csv
import os
import secrets
import hashlib
import smtplib
import sqlite3
from datetime import datetime, timedelta
from email.message import EmailMessage
from db import get_db, init_db
from subscriptions import append_subscription, ensure_csv_has_header, update_send_in_csv
from flask import Flask, render_template, request, redirect, url_for, flash
from unsubscribe import unsubscribe_bp
from email_utils import send_verification_email

app = Flask(
    __name__,
    template_folder="wepages/templates",
    static_folder="webpages/static"
)
app.secret_key = "supersecretkey"  # required for flash messages
init_db()
# ensure CSV migrated/has header
ensure_csv_has_header()
# register unsubscribe blueprint
app.register_blueprint(unsubscribe_bp)

# Ensure DB is initialized before handling requests (compatible with Flask 2 and 3)
def _ensure_db():
    try:
        init_db()
    except Exception:
        app.logger.exception("Database initialization failed during startup")

# Register initializer depending on Flask version
if hasattr(app, "before_first_request"):
    # Older Flask versions provide this decorator
    app.before_first_request(_ensure_db)
else:
    # Flask 3 removed before_first_request; run once on the first request via before_request
    _db_init_done = {"done": False}

    @app.before_request
    def _ensure_db_once():
        if not _db_init_done["done"]:
            _db_init_done["done"] = True
            _ensure_db()

EMAIL_REGEX = r"^[^@]+@[^@]+\.[^@]+$"



@app.route("/signup", methods=["GET", "POST"])
def signup():
    # use UTC ISO timestamp for database 'time' column
    now = datetime.utcnow().isoformat()
    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()

        if not email:
            flash("Email is required.", "error")
            return redirect(url_for("signup"))

        if not re.match(EMAIL_REGEX, email):
            flash("Invalid email address.", "error")
            return redirect(url_for("signup"))

        code = generate_code()
        hashed_code = hash_code(code)
        expires_at = (datetime.utcnow() + timedelta(minutes=10)).isoformat()

        db = get_db()
        # Check whether the email already exists and inspect the 'send' and 'verified' flags
        row = db.execute("SELECT id, send, verified FROM subscribers WHERE email = ?", (email,)).fetchone()
        if row:
            # If already fully verified, tell the user it's registered
            if row["send"] == 1 and row["verified"] == 1:
                db.close()
                flash("This email is already registered.", "error")
                return redirect(url_for("signup"))

            # For existing but not verified emails, (re)issue a verification code, re-enable sending, and redirect to verify
            db.execute("""
                UPDATE subscribers
                SET send = 1,
                    time = ?,
                    verification_code = ?,
                    code_expires_at = ?
                WHERE email = ?
            """, (now, hashed_code, expires_at, email))
            db.commit()
            update_send_in_csv(email, True)
            db.close()
            try:
                send_verification_email(email, code)
            except Exception:
                app.logger.exception("Failed to send verification email for existing subscriber")
                flash("We couldn't send the verification email. Please try again later.", "error")
                return redirect(url_for("signup"))

            flash("Check your email for the verification code.", "info")
            return redirect(url_for("verify", email=email))

        # Not present: insert a new subscriber and send verification code
        try:
            db.execute("""
                INSERT INTO subscribers (
                    email,
                    time,
                    verification_code,
                    code_expires_at,
                    verified
                ) VALUES (?, ?, ?, ?, 0)
            """, (email, now, hashed_code, expires_at))
            db.commit()
            # Add to CSV
            append_subscription(datetime.utcnow().isoformat(), email, True)
            db.close()
            app.logger.info("Reached checkpoint")
            try:
                send_verification_email(email, code)
            except Exception:
                app.logger.exception("Failed to send verification email for new subscriber")
                flash("We couldn't send the verification email. Please try again later.", "error")
                return redirect(url_for("signup"))

            flash("Check your email for the verification code.", "info")
            return redirect(url_for("verify", email=email))

        except sqlite3.IntegrityError as e:
            # UNIQUE constraint failed (race or unexpected state)
            app.logger.warning(f"Duplicate email attempt: {email} | {e}")
            db.close()
            flash("This email is already registered.", "error")
            return redirect(url_for("signup"))

        except sqlite3.OperationalError as e:
            # database is locked, disk I/O errors, etc.
            app.logger.error(f"Database operational error: {e}")
            db.close()
            flash("Our system is busy. Please try again in a moment.", "error")
            return redirect(url_for("signup"))

        except Exception as e:
            app.logger.error(f"SIGNUP ERROR [{email}]: {e}")
            db.close()
            flash("An unexpected error occurred. Please try again.", "error")
            return redirect(url_for("signup"))

    return render_template("signup.html")

@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        code = request.form.get("code", "").strip()

        if not email or not code:
            flash("Email and code are required.", "error")
            return redirect(url_for("verify"))

        hashed = hash_code(code)
        now = datetime.utcnow().isoformat()

        db = get_db()
        row = db.execute("""
            SELECT verification_code, code_expires_at
            FROM subscribers
            WHERE email = ?
        """, (email,)).fetchone()

        if not row:
            flash("Invalid verification attempt.", "error")
            return redirect(url_for("verify"))

        if now > row["code_expires_at"]:
            flash("Verification code expired.", "error")
            return redirect(url_for("verify"))

        if hashed != row["verification_code"]:
            flash("Invalid verification code.", "error")
            return redirect(url_for("verify"))

        db.execute("""
            UPDATE subscribers
            SET verified = 1,
                verification_code = NULL,
                code_expires_at = NULL
            WHERE email = ?
        """, (email,))
        db.commit()
        db.close()

        flash("Email verified successfully!", "success")
        return redirect(url_for("signup"))

    # If redirected from signup, include the email in the form via query string
    email = request.args.get("email", "")
    return render_template("verify.html", email=email)


def generate_code():
    return f"{secrets.randbelow(1_000_000):06d}"

def hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))