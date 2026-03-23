from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str

class TicketResponse(BaseModel):
    id: int
    category: str
    severity: str
    status: str