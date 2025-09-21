from fastapi import FastAPI
from app.routers import emails
from app.database import Base, engine

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title = "AI Email Assistant Backend")

# Include Routers
app.include_router(emails.router, prefix="/emails", tags=['emails'])

@app.get("/health")
def health_check():
    return {"status": "ok"}
