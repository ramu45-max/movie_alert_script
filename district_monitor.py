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
    lower_text = text.lower()

    matches = []

    # Normal keyword checks.
    for keyword in ("VR Mall", "PXL"):
        if keyword.lower() in lower_text:
            matches.append(keyword)

    # Palazzo is special: alert only when its nearby listing contains more
    # than two showtimes. This avoids matching a footer/recommendation link.
    showtime_pattern = r"\b\d{1,2}:\d{2}\s*(?:AM|PM)\b"
    for match in re.finditer(r"Palazzo", text, re.IGNORECASE):
        nearby = text[max(0, match.start() - 300): match.end() + 1800]
        showtime_count = len(re.findall(showtime_pattern, nearby, re.IGNORECASE))
        if showtime_count > 2:
            matches.append(f"Palazzo ({showtime_count} showtimes)")
            break

    if not matches:
        return

    send_email(
        "Spider-Man ticket listing found",
        f"Matching listing(s): {', '.join(matches)}\n\nCheck the page here:\n{URL}",
    )


if __name__ == "__main__":
    main()
