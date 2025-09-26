import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.core.config import settings


def send_email(to_email: str, subject: str, text_body: str = None):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_FROM or settings.SMTP_USER
        msg["To"] = to_email

        part = MIMEText(text_body or "", "plain")
        msg.attach(part)
      
        print(f"Connecting to {settings.SMTP_HOST}...")
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()

        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.sendmail(msg["From"], [to_email], msg.as_string())
        server.quit()

        print(f"Email sent to {to_email}")

    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
