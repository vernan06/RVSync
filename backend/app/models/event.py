"""Event Model"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.classroom import Classroom
from app.models.user import User


class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=True) # NULL = global event
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Event Details
    title = Column(String(255), nullable=False)
    description = Column(Text)
    location = Column(String(255))
    
    # Time Info
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_all_day = Column(Boolean, default=False)
    
    # Event Category
    event_type = Column(String(50), default="other") # exam, assignment, seminar, holiday, activity
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    classroom = relationship("Classroom", back_populates="events")
    creator = relationship("User", back_populates="events_created")
