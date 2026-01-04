import sys
from email_utils import send_verification_email


def main():
    to = sys.argv[1] if len(sys.argv) > 1 else input("Send test email to: ").strip()
    code = "123456"
    try:
        send_verification_email(to, code)
        print("Sent OK")
    except Exception as e:
        print("Send failed:", e)


if __name__ == "__main__":
    main()
