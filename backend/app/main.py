from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from collections import Counter
from app.database import SessionLocal
from app import models
from app.schemas import EmailBase, EmailStats
import sqlite3

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, Email Assistant is running!"}

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/emails", response_model=list[EmailBase])
def get_emails(db: Session = Depends(get_db)):
    return db.query(models.Email).all()

# Get recent emails
@app.get("/emails/recent")
def get_recent_emails(limit: int = 5):
    try:
        conn = sqlite3.connect("emails.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM emails ORDER BY date DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()

        emails = []
        for row in rows:
            emails.append({
                "id": row[0],
                "subject": row[1],
                "sender": row[2],
                "date": row[3],
                "body": row[4]
            })

        return {"recent_emails": emails}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/emails/{email_id}", response_model=EmailBase)
def get_email(email_id: int, db: Session = Depends(get_db)):
    email = db.query(models.Email).filter(models.Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email


@app.get("/emails/stats", response_model=EmailStats)
def get_email_stats(db: Session = Depends(get_db)):
    emails = db.query(models.Email).all()
    total_emails = len(emails)
    filtered_emails = len([e for e in emails if e.is_filtered])
    sentiment_distribution = Counter([e.sentiment for e in emails if e.sentiment])
    priority_distribution = Counter([e.priority for e in emails if e.priority])

    return {
        "total_emails": total_emails,
        "filtered_emails": filtered_emails,
        "sentiment_distribution": dict(sentiment_distribution),
        "priority_distribution": dict(priority_distribution),
    }


