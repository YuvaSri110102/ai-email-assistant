from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float
from datetime import datetime
from app.database import Base

class Email(Base):
    __tablename__ = "emails"
    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String, index=True)
    subject = Column(String, index=True)
    body = Column(Text)
    date = Column(DateTime, default=datetime.utcnow)
    is_filtered = Column(Boolean, default=False)
    sentiment = Column(String, default=None)
    priority = Column(String, default="normal")
    category = Column(String, default="other")
    sentiment_score = Column(Float, default=None)
    summary = Column(Text, nullable=True)
    topics = Column(Text, nullable=True)
