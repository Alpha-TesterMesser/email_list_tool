from flask import Blueprint, render_template, request, redirect, url_for, flash
import re
import sqlite3
from db import get_db
from subscriptions import update_send_in_csv

unsubscribe_bp = Blueprint("unsubscribe", __name__)

EMAIL_REGEX = r"^[^@]+@[^@]+\.[^@]+$"


@unsubscribe_bp.route("/unsubscribe", methods=["GET", "POST"])
def unsubscribe():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        if not email:
            flash("Email is required.", "error")
            return redirect(url_for("unsubscribe.unsubscribe"))
        if not re.match(EMAIL_REGEX, email):
            flash("Please enter a valid email address.", "error")
            return redirect(url_for("unsubscribe.unsubscribe"))

        db = None
        try:
            db = get_db()
            # Get the row including the 'send' status
            cur = db.execute("SELECT id, send FROM subscribers WHERE email = ?", (email,))
            row = cur.fetchone()
            if not row:
                flash("That email is not on our list.", "error")
            elif row["send"] == 0:
                flash("You're already unsubscribed.", "info")
            else:
                db.execute("UPDATE subscribers SET send = 0 WHERE email = ?", (email,))
                db.commit()
                update_send_in_csv(email, False)
                flash("You're unsubscribed.", "success")
        except sqlite3.DatabaseError:
            # Catch broader DB errors
            flash("Database error. Please try again later.", "error")
        finally:
            if db:
                db.close()
        return redirect(url_for("unsubscribe.unsubscribe"))

    return render_template("unsubscribe.html")
