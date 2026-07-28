import os
import re
import smtplib
from email.message import EmailMessage

import requests


URL = "https://www.district.in/movies/spider-man-brand-new-day-movie-tickets-in-chennai-MV194537?frmtid=RRFdpndyPD"
TO_EMAIL = "ramunaathan45@gmail.com"


def send_email(subject: str, body: str) -> None:
    sender = os.environ["EMAIL_ADDRESS"]
    password = os.environ["EMAIL_APP_PASSWORD"]

    message = EmailMessage()
    message["From"] = sender
    message["To"] = TO_EMAIL
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(message)


def main() -> None:
    response = requests.get(
        URL,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30,
    )
    response.raise_for_status()
    text = re.sub(r"\s+", " ", response.text)

    keywords = ("VR Mall", "PVR Palazzo", "Palazzo", "PXL")
    matches = [keyword for keyword in keywords if keyword.lower() in text.lower()]
    if not matches:
        return

    send_email(
        "Spider-Man ticket listing found",
        f"Matching listing keyword(s): {', '.join(matches)}\n\nCheck the page here:\n{URL}",
    )


if __name__ == "__main__":
    main()
