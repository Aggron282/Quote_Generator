# utils/send_email.py

import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("SMTP_EMAIL")
PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def send_email(to_email, subject, body):
    """Send a basic plain text email."""
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL, PASSWORD)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(EMAIL, to_email, message)
            print(f"Plain email sent to {to_email}")
    except Exception as e:
        print(f"Error sending plain email to {to_email}: {e}")


def send_html_email_with_attachment(to_email, subject, html_body, attachments=[]):
    """Send an HTML email with optional attachments."""
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL
    msg['To'] = to_email

    msg.set_content("This email contains an HTML version. Please view it in an HTML-compatible email client.")
    msg.add_alternative(html_body, subtype='html')

    for file_path in attachments:
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
                file_name = os.path.basename(file_path)
                msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)
        except Exception as e:
            print(f"Error attaching file {file_path}: {e}")

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL, PASSWORD)
            server.send_message(msg)
            print(f"HTML email sent to {to_email}")
    except Exception as e:
        print(f"Error sending HTML email to {to_email}: {e}")
