from app.database import SessionLocal, Base, engine
from app.models import Email

Base.metadata.create_all(bind=engine)

# Simple word lists for sentiment and priority
POSITIVE_WORDS = ["thank you", "great", "appreciate", "happy", "good"]
NEGATIVE_WORDS = ["problem", "issue", "not working", "frustrated", "angry", "cannot"]
URGENT_KEYWORDS = ["immediately", "critical", "cannot access", "urgent", "asap"]

# Start DB session
db = SessionLocal()

emails = db.query(Email).filter(Email.is_filtered == True).all()

for email in emails:
    text = (email.subject + " " + email.body).lower()

    # Sentiment detection
    if any(word in text for word in NEGATIVE_WORDS):
        email.sentiment = "Negative"
    elif any(word in text for word in POSITIVE_WORDS):
        email.sentiment = "Positive"
    else:
        email.sentiment = "Neutral"

    # Priority detection
    if any(word in text for word in URGENT_KEYWORDS):
        email.priority = "Urgent"
    else:
        email.priority = "Not Urgent"

    db.add(email)

db.commit()
db.close()
print("✅ Emails categorized and prioritized successfully!")