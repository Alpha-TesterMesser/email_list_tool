import logging
import smtplib
import os
from email.message import EmailMessage

log = logging.getLogger(__name__)

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")


def send_verification_email(to_email, code):
    """Send a verification email via Gmail SMTP. Raises RuntimeError when credentials are missing and re-raises other exceptions so callers can react."""
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        log.error("Email credentials not configured. Set GMAIL_USER and GMAIL_APP_PASSWORD environment variables.")
        raise RuntimeError("Email credentials not configured")

    msg = EmailMessage()
    msg["From"] = GMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = "Your Verification Code"

    msg.set_content(f"""
Hi!

Your verification code is:

{code}

This code will expire in 10 minutes.

If you did not request this, you can safely ignore this email.
""")

    try:
        log.info("Sending verification email to %s", to_email)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            smtp.send_message(msg)
        log.info("Verification email sent to %s", to_email)
    except Exception:
        log.exception("Failed to send verification email to %s", to_email)
        raise
    