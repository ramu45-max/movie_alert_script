import os
import re
import smtplib
from email.message import EmailMessage

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


URL = "https://www.district.in/movies/spider-man-brand-new-day-movie-tickets-in-chennai-MV194537?frmtid=RRFdpndyPD"
TO_EMAIL = "ramunaathan45@gmail.com"

# Add or remove keywords here when testing locally.
# Example: "Ampa" will match any cinema listing containing Ampa.
INITIALIZING_KEYWORDS = [
    "VR Mall",
    "PVR Palazzo",
    "Palazzo",
    "PXL",
     "Ampa",  # uncomment this line for testing
]


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
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1440,1600")

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(URL)
        WebDriverWait(driver, 30).until(
            lambda browser: browser.find_elements(
                By.CSS_SELECTOR, 'li[class*="movieSessions"]'
            )
        )
        listing_items = driver.find_elements(
            By.CSS_SELECTOR, 'li[class*="movieSessions"]'
        )

        listing_texts = [
            " ".join(item.text.split())
            for item in listing_items
            if re.search(r"\b\d{1,2}:\d{2}\s*(?:AM|PM)\b", item.text, re.IGNORECASE)
        ]
    finally:
        driver.quit()

    configured = os.getenv("MATCH_KEYWORDS")
    keywords = (
        [word.strip() for word in configured.split(",") if word.strip()]
        if configured
        else INITIALIZING_KEYWORDS
    )
    matches = []
    for text in listing_texts:
        found = [keyword for keyword in keywords if re.search(re.escape(keyword), text, re.IGNORECASE)]
        if found:
            matches.append(f"{', '.join(found)}: {text[:500]}")

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
