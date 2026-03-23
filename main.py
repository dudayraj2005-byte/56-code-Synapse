from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import Base, engine
from routes import chat, ticket

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(chat.router)
app.include_router(ticket.router)

# Serve frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.get("/api")
def home():
    return {"message": "Smart Complaint System API running 🚀"}