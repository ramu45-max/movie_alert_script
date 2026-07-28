import os
import re
import smtplib
from email.message import EmailMessage

import requests
from bs4 import BeautifulSoup


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
    soup = BeautifulSoup(response.text, "html.parser")
    listing_texts = []

    # Only inspect venue/showtime listing containers. This avoids matching
    # generic footer links such as "PVR Palazzo" elsewhere on the page.
    for link in soup.find_all("a"):
        label = link.get_text(" ", strip=True)
        if not re.search(r"VR Mall|Palazzo|PXL", label, re.IGNORECASE):
            continue

        node = link
        for _ in range(6):
            text = re.sub(r"\s+", " ", node.get_text(" ", strip=True))
            has_showtime = re.search(r"\b\d{1,2}:\d{2}\s*(?:AM|PM)\b", text, re.IGNORECASE)
            if has_showtime:
                listing_texts.append(text)
                break
            node = node.parent
            if node is None:
                break

    # PXL may be rendered without a separate venue link; only accept it when
    # it appears in a block that also contains a showtime.
    for node in soup.find_all(string=re.compile(r"PXL", re.IGNORECASE)):
        parent = node.parent
        if parent:
            text = re.sub(r"\s+", " ", parent.parent.get_text(" ", strip=True))
            if re.search(r"\b\d{1,2}:\d{2}\s*(?:AM|PM)\b", text, re.IGNORECASE):
                listing_texts.append(text)

    matches = []
    for text in listing_texts:
        for keyword in ("VR Mall", "PVR Palazzo", "Palazzo", "PXL", "Ampa"):
            if re.search(re.escape(keyword), text, re.IGNORECASE):
                matches.append(f"{keyword}: {text[:500]}")

    if not matches:
        return

    send_email(
        "Spider-Man ticket listing found",
        "Matching listing(s):\n"
        + "\n\n".join(dict.fromkeys(matches))
        + f"\n\nCheck the page here:\n{URL}",
    )


if __name__ == "__main__":
    main()
