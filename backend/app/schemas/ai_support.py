from pydantic import BaseModel
from typing import Optional, List

class ChatRequest(BaseModel):
    message: str
    context: Optional[dict] = None

class ChatResponse(BaseModel):
    response: str
    is_success: bool = True
