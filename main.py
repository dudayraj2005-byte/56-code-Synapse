from fastapi import FastAPI
from database import Base, engine
from routes import chat, ticket

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(chat.router)
app.include_router(ticket.router)

@app.get("/")
def home():
    return {"message": "Smart Complaint System API running 🚀"}