from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Email

router = APIRouter()

@router.get("/")
def get_emails(db: Session = Depends(get_db)):
    emails = db.query(Email).all()
    return emails
