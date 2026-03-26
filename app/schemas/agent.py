from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class AgentBase(BaseModel):
    name: str = Field(..., max_length=100)
    system_prompt: str = Field(..., max_length=5000)
    voice_id: Optional[str] = "alloy"

class AgentCreate(AgentBase):
    pass

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    system_prompt: Optional[str] = None
    voice_id: Optional[str] = None

class AgentResponse(AgentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    audio_url: Optional[str] = None

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    audio_path: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class SessionResponse(BaseModel):
    id: int
    agent_id: int
    created_at: datetime
    messages: List[MessageResponse] = []
    
    class Config:
        from_attributes = True
