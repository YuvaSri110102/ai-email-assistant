from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.database import Base

class Email(Base):
    __tablename__ = "emails"
    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String, index=True)
    subject = Column(String, index=True)
    body = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    is_filtered = Column(Boolean, default=False)
    sentiment = Column(String, default="Neutral")
    priority = Column(String, default="Not Urgent")
    
