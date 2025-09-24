from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from collections import Counter
from app.database import SessionLocal, engine, Base
from app import models, schemas
from app.models import Email
from app.schemas import EmailBase, EmailStats
from app.utils.sentiment_analyzer import analyze_sentiment
import sqlite3
from transformers import pipeline

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


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

@app.get("/emails", response_model=list[schemas.EmailResponse])
def get_emails(db: Session = Depends(get_db)):
    return db.query(models.Email).all()

# Get recent emails
@app.get("/emails/recent", response_model=list[schemas.EmailResponse])
def get_recent_emails(db: Session = Depends(get_db)):
    return db.query(models.Email).order_by(models.Email.date.desc()).limit(5).all()

# Get urgent emails
@app.get("/emails/urgent", response_model=list[schemas.EmailResponse])
def get_urgent_emails(db: Session = Depends(get_db)):
    return db.query(models.Email).filter(models.Email.priority == "urgent").all()

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

@app.get("/emails/{email_id}/sentiment")
def get_email_sentiment(email_id: int):
    db = SessionLocal()
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        db.close()
        raise HTTPException(status_code=404, detail="Email not found")

    sentiment, score = analyze_sentiment(email.body or email.subject)
    email.sentiment = sentiment
    email.sentiment_score = score
    db.commit()

    response = {
        "id": email.id,
        "sentiment": sentiment,
        "score": score
    }
    db.close()
    return response

@app.get("/emails/sentiment/{sentiment}")
def get_email_by_sentiment(sentiment: str):
    conn = sqlite3.connect("emails.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, subject, sender, date, sentiment, sentiment_score FROM emails WHERE sentiment = ?",
        (sentiment,)
    )
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": r[0],
            "subject": r[1],
            "sender": r[2],
            "date": r[3],
            "sentiment": r[4],
            "score": r[5],
        }
        for r in rows
    ]

@app.get("/emails/search")
def search_emails(q: str):
    conn = sqlite3.connect("emails.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, subject, sender, date, sentiment, sentiment_score FROM emails WHERE subject LIKE ? OR body LIKE ?",
        (f"%{q}%", f"%{q}%")
    )
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": r[0],
            "subject": r[1],
            "sender": r[2],
            "date": r[3],
            "sentiment": r[4],
            "score": r[5],
        }
        for r in rows
    ]

@app.get("/emails/{email_id}", response_model=EmailBase)
def get_email(email_id: int, db: Session = Depends(get_db)):
    email = db.query(models.Email).filter(models.Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email


@app.get("/emails/{email_id}/summary")
def summarize_email(email_id: int, db: Session = Depends(get_db)):
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    # Text = subject + body
    text = (email.subject or "") + " " + (email.body or "")
    if not text.strip():
        return {"id": email_id, "summary": "No content available"}
    
    summary = summarizer(text, max_length=60, min_length=10, do_sample=False)
    
    return {
        "id": email_id,
        "summary": summary[0]["summary_text"]
    }
