"""Chat Router with WebSocket Support"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Dict
import json

from app.database import get_db, SessionLocal
from app.models.user import User
from app.models.chat import ChatMessage
from app.schemas.chat import MessageCreate, MessageResponse, ConversationResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/messages", tags=["Chat"])

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[str(user_id)] = websocket
    
    def disconnect(self, user_id: int):
        self.active_connections.pop(str(user_id), None)
    
    async def send_personal_message(self, message: dict, user_id: int):
        connection = self.active_connections.get(str(user_id))
        if connection:
            await connection.send_json(message)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)


manager = ConnectionManager()


@router.post("/send", response_model=MessageResponse)
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message to another user"""
    # Verify recipient exists
    recipient = db.query(User).filter(User.id == message_data.to_user_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    
    message = ChatMessage(
        from_user_id=current_user.id,
        to_user_id=message_data.to_user_id,
        message=message_data.message,
        message_type=message_data.message_type
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    
    # Send via WebSocket if recipient is connected
    msg_data = {
        "id": message.id,
        "from_user_id": current_user.id,
        "sender_name": current_user.name,
        "message": message.message,
        "created_at": message.created_at.isoformat()
    }
    await manager.send_personal_message(msg_data, message_data.to_user_id)
    
    return MessageResponse(
        id=message.id,
        from_user_id=message.from_user_id,
        to_user_id=message.to_user_id,
        message=message.message,
        message_type=message.message_type,
        is_read=message.is_read,
        created_at=message.created_at,
        sender_name=current_user.name
    )


@router.get("/inbox/{user_id}", response_model=List[ConversationResponse])
async def get_inbox(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of conversations for a user"""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get all unique conversation partners
    from sqlalchemy import or_, func
    
    sent = db.query(ChatMessage.to_user_id.label('partner_id')).filter(
        ChatMessage.from_user_id == user_id
    )
    received = db.query(ChatMessage.from_user_id.label('partner_id')).filter(
        ChatMessage.to_user_id == user_id
    )
    partners = sent.union(received).distinct().all()
    
    conversations = []
    for (partner_id,) in partners:
        partner = db.query(User).filter(User.id == partner_id).first()
        if not partner:
            continue
        
        # Get last message
        last_msg = db.query(ChatMessage).filter(
            or_(
                (ChatMessage.from_user_id == user_id) & (ChatMessage.to_user_id == partner_id),
                (ChatMessage.from_user_id == partner_id) & (ChatMessage.to_user_id == user_id)
            )
        ).order_by(ChatMessage.created_at.desc()).first()
        
        # Count unread
        unread = db.query(ChatMessage).filter(
            ChatMessage.from_user_id == partner_id,
            ChatMessage.to_user_id == user_id,
            ChatMessage.is_read == False
        ).count()
        
        if last_msg:
            conversations.append(ConversationResponse(
                user_id=partner_id,
                user_name=partner.name,
                last_message=last_msg.message[:50],
                last_message_time=last_msg.created_at,
                unread_count=unread
            ))
    
    # Sort by last message time
    conversations.sort(key=lambda x: x.last_message_time, reverse=True)
    return conversations


@router.get("/conversation/{user1_id}/{user2_id}", response_model=List[MessageResponse])
async def get_conversation(
    user1_id: int,
    user2_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversation between two users"""
    if current_user.id not in [user1_id, user2_id]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    from sqlalchemy import or_
    
    messages = db.query(ChatMessage).filter(
        or_(
            (ChatMessage.from_user_id == user1_id) & (ChatMessage.to_user_id == user2_id),
            (ChatMessage.from_user_id == user2_id) & (ChatMessage.to_user_id == user1_id)
        )
    ).order_by(ChatMessage.created_at).all()
    
    # Mark messages as read
    for msg in messages:
        if msg.to_user_id == current_user.id and not msg.is_read:
            msg.is_read = True
            msg.read_at = datetime.utcnow()
    db.commit()
    
    result = []
    for msg in messages:
        sender = db.query(User).filter(User.id == msg.from_user_id).first()
        result.append(MessageResponse(
            id=msg.id,
            from_user_id=msg.from_user_id,
            to_user_id=msg.to_user_id,
            message=msg.message,
            message_type=msg.message_type,
            is_read=msg.is_read,
            created_at=msg.created_at,
            sender_name=sender.name if sender else None
        ))
    return result


@router.websocket("/ws/chat/{from_id}/{to_id}")
async def websocket_chat(websocket: WebSocket, from_id: int, to_id: int):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket, from_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Save message to database
            db = SessionLocal()
            try:
                sender = db.query(User).filter(User.id == from_id).first()
                message = ChatMessage(
                    from_user_id=from_id,
                    to_user_id=to_id,
                    message=message_data.get("message", ""),
                    message_type=message_data.get("type", "text")
                )
                db.add(message)
                db.commit()
                db.refresh(message)
                
                # Send to recipient
                msg_response = {
                    "id": message.id,
                    "from_user_id": from_id,
                    "sender_name": sender.name if sender else "Unknown",
                    "message": message.message,
                    "created_at": message.created_at.isoformat()
                }
                await manager.send_personal_message(msg_response, to_id)
                
                # Echo back to sender
                await websocket.send_json(msg_response)
            finally:
                db.close()
    except WebSocketDisconnect:
        manager.disconnect(from_id)
