"""Announcements Router"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.classroom import ClassroomEnrollment
from app.models.chat import Announcement, AnnouncementRead
from app.schemas.chat import AnnouncementCreate, AnnouncementResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/announcement", tags=["Announcements"])


@router.post("/create", response_model=AnnouncementResponse)
async def create_announcement(
    announcement_data: AnnouncementCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new announcement"""
    # If classroom-specific, verify instructor role
    if announcement_data.classroom_id:
        enrollment = db.query(ClassroomEnrollment).filter(
            ClassroomEnrollment.classroom_id == announcement_data.classroom_id,
            ClassroomEnrollment.user_id == current_user.id,
            ClassroomEnrollment.role == "instructor"
        ).first()
        if not enrollment:
            raise HTTPException(status_code=403, detail="Only instructors can create announcements")
    
    announcement = Announcement(
        classroom_id=announcement_data.classroom_id,
        user_id=current_user.id,
        title=announcement_data.title,
        content=announcement_data.content,
        priority=announcement_data.priority,
        is_pinned=announcement_data.is_pinned
    )
    db.add(announcement)
    db.commit()
    db.refresh(announcement)
    
    return AnnouncementResponse(
        id=announcement.id,
        classroom_id=announcement.classroom_id,
        user_id=announcement.user_id,
        title=announcement.title,
        content=announcement.content,
        priority=announcement.priority,
        is_pinned=announcement.is_pinned,
        created_at=announcement.created_at,
        author_name=current_user.name,
        is_read=False
    )


@router.get("/list/{classroom_id}", response_model=List[AnnouncementResponse])
async def list_announcements(
    classroom_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List announcements for a classroom"""
    # Verify enrollment
    enrollment = db.query(ClassroomEnrollment).filter(
        ClassroomEnrollment.classroom_id == classroom_id,
        ClassroomEnrollment.user_id == current_user.id
    ).first()
    if not enrollment:
        raise HTTPException(status_code=403, detail="Not enrolled in this classroom")
    
    announcements = db.query(Announcement).filter(
        Announcement.classroom_id == classroom_id
    ).order_by(Announcement.is_pinned.desc(), Announcement.created_at.desc()).all()
    
    result = []
    for a in announcements:
        author = db.query(User).filter(User.id == a.user_id).first()
        read_status = db.query(AnnouncementRead).filter(
            AnnouncementRead.announcement_id == a.id,
            AnnouncementRead.user_id == current_user.id
        ).first()
        
        result.append(AnnouncementResponse(
            id=a.id,
            classroom_id=a.classroom_id,
            user_id=a.user_id,
            title=a.title,
            content=a.content,
            priority=a.priority,
            is_pinned=a.is_pinned,
            created_at=a.created_at,
            author_name=author.name if author else None,
            is_read=read_status is not None
        ))
    
    return result


@router.get("/global", response_model=List[AnnouncementResponse])
async def list_global_announcements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List institution-wide announcements"""
    announcements = db.query(Announcement).filter(
        Announcement.classroom_id == None
    ).order_by(Announcement.is_pinned.desc(), Announcement.created_at.desc()).limit(20).all()
    
    result = []
    for a in announcements:
        author = db.query(User).filter(User.id == a.user_id).first()
        read_status = db.query(AnnouncementRead).filter(
            AnnouncementRead.announcement_id == a.id,
            AnnouncementRead.user_id == current_user.id
        ).first()
        
        result.append(AnnouncementResponse(
            id=a.id,
            classroom_id=a.classroom_id,
            user_id=a.user_id,
            title=a.title,
            content=a.content,
            priority=a.priority,
            is_pinned=a.is_pinned,
            created_at=a.created_at,
            author_name=author.name if author else None,
            is_read=read_status is not None
        ))
    
    return result


@router.put("/{announcement_id}/read")
async def mark_as_read(
    announcement_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark an announcement as read"""
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    # Check if already read
    existing = db.query(AnnouncementRead).filter(
        AnnouncementRead.announcement_id == announcement_id,
        AnnouncementRead.user_id == current_user.id
    ).first()
    
    if not existing:
        read_record = AnnouncementRead(
            announcement_id=announcement_id,
            user_id=current_user.id
        )
        db.add(read_record)
        db.commit()
    
    return {"message": "Marked as read"}
