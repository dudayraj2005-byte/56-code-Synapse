from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
import models

router = APIRouter()

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 📋 Get all tickets
@router.get("/tickets")
def get_tickets(db: Session = Depends(get_db)):
    return db.query(models.Ticket).all()


# 📊 Get stats (NEW)
@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    tickets = db.query(models.Ticket).all()

    total = len(tickets)

    high = len([t for t in tickets if t.severity == "High"])
    medium = len([t for t in tickets if t.severity == "Medium"])
    low = len([t for t in tickets if t.severity == "Low"])

    return {
        "total": total,
        "high": high,
        "medium": medium,
        "low": low
    }