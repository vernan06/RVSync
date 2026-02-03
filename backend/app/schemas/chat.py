"""Chat and Communication Schemas"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# Chat Schemas
class MessageCreate(BaseModel):
    to_user_id: int
    message: str
    message_type: str = "text"


class MessageResponse(BaseModel):
    id: int
    from_user_id: int
    to_user_id: int
    message: str
    message_type: str
    is_read: bool
    created_at: datetime
    sender_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    user_id: int
    user_name: str
    last_message: str
    last_message_time: datetime
    unread_count: int = 0


# Announcement Schemas
class AnnouncementCreate(BaseModel):
    classroom_id: Optional[int] = None  # NULL = institution-wide
    title: str
    content: str
    priority: str = "normal"
    is_pinned: bool = False


class AnnouncementResponse(BaseModel):
    id: int
    classroom_id: Optional[int] = None
    user_id: int
    title: str
    content: str
    priority: str
    is_pinned: bool
    created_at: datetime
    author_name: Optional[str] = None
    is_read: bool = False
    
    class Config:
        from_attributes = True
