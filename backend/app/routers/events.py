"""Events Router"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.database import get_db
from app.models.event import Event
from app.models.user import User
from app.models.classroom import ClassroomEnrollment
from app.schemas.event import EventCreate, EventResponse, EventUpdate
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/events", tags=["Events"])


@router.post("/", response_model=EventResponse)
async def create_event(
    event_data: EventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new event"""
    # Permission check: If classroom_id is provided, check if user is instructor or admin
    if event_data.classroom_id:
        enrollment = db.query(ClassroomEnrollment).filter(
            ClassroomEnrollment.classroom_id == event_data.classroom_id,
            ClassroomEnrollment.user_id == current_user.id
        ).first()
        
        if not current_user.is_admin and (not enrollment or enrollment.role != "instructor"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only instructors or admins can create classroom events"
            )

    event = Event(
        **event_data.model_dump(),
        created_by=current_user.id
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/my", response_model=List[EventResponse])
async def get_my_events(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all events relevant to the current user (global + their classrooms)"""
    classroom_ids = [e.classroom_id for e in current_user.enrollments]
    
    events = db.query(Event).filter(
        (Event.classroom_id == None) | (Event.classroom_id.in_(classroom_ids))
    ).order_by(Event.start_time.asc()).all()
    
    return events


@router.get("/classroom/{classroom_id}", response_model=List[EventResponse])
async def get_classroom_events(
    classroom_id: int,
    db: Session = Depends(get_db)
):
    """Get events for a specific classroom"""
    events = db.query(Event).filter(Event.classroom_id == classroom_id).order_by(Event.start_time.asc()).all()
    return events


@router.get("/upcoming", response_model=List[EventResponse])
async def get_upcoming_events(
    limit: int = 5,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get upcoming events for the current user"""
    classroom_ids = [e.classroom_id for e in current_user.enrollments]
    now = datetime.utcnow()
    
    events = db.query(Event).filter(
        ((Event.classroom_id == None) | (Event.classroom_id.in_(classroom_ids))),
        Event.end_time >= now
    ).order_by(Event.start_time.asc()).limit(limit).all()
    
    return events


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: int, db: Session = Depends(get_db)):
    """Get event by ID"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event_data: EventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an event"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
        
    if event.created_by != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to update this event")
        
    update_data = event_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(event, key, value)
        
    db.commit()
    db.refresh(event)
    return event


@router.delete("/{event_id}")
async def delete_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an event"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
        
    if event.created_by != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this event")
        
    db.delete(event)
    db.commit()
    return {"message": "Event deleted successfully"}
