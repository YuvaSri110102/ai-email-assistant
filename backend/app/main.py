from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from collections import Counter
from app.database import SessionLocal, engine, Base
from app import models, schemas
from app.schemas import EmailBase, EmailStats
from app.sentiment_analyzer import analyze_sentiment
import sqlite3

models.Base.metadata.create_all(bind=engine)

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

@app.get("/emails/{email_id}/sentiment")
def get_email_sentiment(email_id: int):
    try:
        conn = sqlite3.connect("emails.db")
        cursor = conn.cursor()
        cursor.execute("SELECT body FROM emails WHERE id = ?", (email_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Email not found")

        body = row[0]
        sentiment = analyze_sentiment(body)

        return {"email_id": email_id, "sentiment": sentiment}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

