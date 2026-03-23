from sqlalchemy import Column, Integer, String, Text
from database import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String)
    age = Column(Integer)
    user_message = Column(Text)
    category = Column(String)
    severity = Column(String)
    status = Column(String, default="open")