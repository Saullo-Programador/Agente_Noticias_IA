"""
Envia reports/latest.md por e-mail via SMTP.
"""

import os
import smtplib
from datetime import date
from email.mime.text import MIMEText

REQUIRED_VARS = ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASS", "EMAIL_TO"]


def send():
    missing = [v for v in REQUIRED_VARS if not os.environ.get(v)]
    if missing:
        print(f"[info] envio de e-mail pulado, faltando: {', '.join(missing)}")
        return

    with open("reports/latest.md", encoding="utf-8") as f:
        body = f.read()

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = f"Radar de IA - {date.today().isoformat()}"
    msg["From"] = os.environ["SMTP_USER"]
    msg["To"] = os.environ["EMAIL_TO"]

    with smtplib.SMTP(os.environ["SMTP_HOST"], int(os.environ["SMTP_PORT"])) as server:
        server.starttls()
        server.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])
        server.sendmail(os.environ["SMTP_USER"], [os.environ["EMAIL_TO"]], msg.as_string())

    print(f"E-mail enviado para {os.environ['EMAIL_TO']}")


if __name__ == "__main__":
    send()
