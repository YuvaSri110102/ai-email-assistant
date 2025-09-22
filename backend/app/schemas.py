from pydantic import BaseModel
from datetime import datetime

class EmailBase(BaseModel):
    id: int
    sender: str
    subject: str
    body: str
    date: datetime
    is_filtered: bool
    sentiment: str | None = None
    priority: str | None = None

    class Config:
        orm_mode = True
    

class EmailStats(BaseModel):
    total_emails: int
    filtered_emails: int
    sentiment_distribution: dict
    priority_distribution: dict
