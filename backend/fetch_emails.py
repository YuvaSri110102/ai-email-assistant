from app.config import EMAIL_PASS, EMAIL_USER, IMAP_SERVER, IMAP_PORT
from imapclient import IMAPClient
import pyzmail
from app.database import SessionLocal, Base, engine
from app.models import Email
from datetime import datetime
import ssl

# Ensure tables exist
Base.metadata.create_all(bind=engine)

def categorize_email(subject: str, body: str):
    text = (subject + " " + body).lower()

    # Priority detection
    urgent_keywords = ["immediately", "urgent", "asap", "critical", "cannot access"]
    priority = "urgent" if any(k in text for k in urgent_keywords) else "normal"

    # Category detection
    if any(k in text for k in ["support", "issue", "error"]):
        category = "support"
    elif any(k in text for k in ["query", "question", "info"]):
        category = "query"
    elif any(k in text for k in ["request", "feature", "need"]):
        category = "request"
    elif any(k in text for k in ["help", "assist", "guidance"]):
        category = "help"
    else:
        category = "other"

    return priority, category


def fetch_and_store_emails():
    context = ssl.create_default_context()

    with IMAPClient(IMAP_SERVER, port=IMAP_PORT, ssl_context=context) as client:
        client.login(EMAIL_USER, EMAIL_PASS)
        client.select_folder("INBOX", readonly=True)

        # Fetch last 20 emails
        messages = client.search(["ALL"])
        messages = messages[-20:]

        db = SessionLocal()

        for msgid, data in client.fetch(messages, ["ENVELOPE", "RFC822"]).items():
            try:
                envelope = data[b"ENVELOPE"]
                raw_message = data[b"RFC822"]
                message = pyzmail.PyzMessage.factory(raw_message)

                subject = message.get_subject() or ""
                sender = (
                    envelope.from_[0].mailbox.decode()
                    + "@"
                    + envelope.from_[0].host.decode()
                )

                # Safely extract body (prefer text, fallback to HTML)
                if message.text_part:
                    body = message.text_part.get_payload().decode(
                        message.text_part.charset
                    )
                elif message.html_part:
                    body = message.html_part.get_payload().decode(
                        message.html_part.charset
                    )
                else:
                    body = ""

                date = envelope.date or datetime.utcnow()

                # Keyword filter
                keywords = ["support", "query", "request", "help"]
                is_filtered = any(k.lower() in subject.lower() for k in keywords)

                # Priority + category
                priority, category = categorize_email(subject, body)

                email_obj = Email(
                    sender=sender,
                    subject=subject,
                    body=body,
                    date=date,
                    is_filtered=is_filtered,
                    priority=priority,
                    category=category,
                )
                db.add(email_obj)

            except Exception as e:
                print(f"⚠️ Skipped one email (ID {msgid}) due to error: {e}")

        db.commit()
        db.close()
        print("✅ Fetched, categorized, and saved emails successfully!")


if __name__ == "__main__":
    fetch_and_store_emails()
