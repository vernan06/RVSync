"""Classroom Router"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.models.classroom import Classroom, ClassroomEnrollment, StudyGroup, StudyGroupMember
from app.schemas.classroom import (
    ClassroomCreate, ClassroomResponse, ClassroomHub,
    EnrollmentCreate, EnrollmentResponse,
    StudyGroupCreate, StudyGroupResponse
)
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/classroom", tags=["Classrooms"])


@router.post("/create", response_model=ClassroomResponse)
async def create_classroom(
    classroom_data: ClassroomCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new classroom"""
    # Check for duplicate code
    existing = db.query(Classroom).filter(Classroom.code == classroom_data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Classroom code already exists")
    
    classroom = Classroom(
        name=classroom_data.name,
        code=classroom_data.code,
        description=classroom_data.description,
        branch=classroom_data.branch,
        year_level=classroom_data.year_level,
        semester=classroom_data.semester,
        section=classroom_data.section,
        max_students=classroom_data.max_students,
        created_by=current_user.id
    )
    db.add(classroom)
    db.commit()
    db.refresh(classroom)
    
    # Auto-enroll creator as instructor
    enrollment = ClassroomEnrollment(
        classroom_id=classroom.id,
        user_id=current_user.id,
        role="instructor"
    )
    db.add(enrollment)
    db.commit()
    
    return ClassroomResponse(
        id=classroom.id,
        name=classroom.name,
        code=classroom.code,
        description=classroom.description,
        branch=classroom.branch,
        year_level=classroom.year_level,
        semester=classroom.semester,
        section=classroom.section,
        max_students=classroom.max_students,
        created_by=classroom.created_by,
        created_at=classroom.created_at,
        student_count=1
    )


@router.get("/{classroom_id}", response_model=ClassroomResponse)
async def get_classroom(classroom_id: int, db: Session = Depends(get_db)):
    """Get classroom by ID"""
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    student_count = db.query(ClassroomEnrollment).filter(
        ClassroomEnrollment.classroom_id == classroom_id
    ).count()
    
    return ClassroomResponse(
        id=classroom.id,
        name=classroom.name,
        code=classroom.code,
        description=classroom.description,
        branch=classroom.branch,
        year_level=classroom.year_level,
        semester=classroom.semester,
        section=classroom.section,
        max_students=classroom.max_students,
        created_by=classroom.created_by,
        created_at=classroom.created_at,
        student_count=student_count
    )


@router.get("/{classroom_id}/hub", response_model=ClassroomHub)
async def get_classroom_hub(
    classroom_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get classroom hub with all details"""
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    # Verify enrollment
    enrollment = db.query(ClassroomEnrollment).filter(
        ClassroomEnrollment.classroom_id == classroom_id,
        ClassroomEnrollment.user_id == current_user.id
    ).first()
    if not enrollment:
        raise HTTPException(status_code=403, detail="Not enrolled in this classroom")
    
    # Get members
    enrollments = db.query(ClassroomEnrollment).filter(
        ClassroomEnrollment.classroom_id == classroom_id
    ).all()
    members = []
    for e in enrollments:
        user = db.query(User).filter(User.id == e.user_id).first()
        if user:
            members.append({
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": e.role,
                "profile_image": user.profile_image
            })
    
    # Get courses
    courses = [
        {
            "id": c.id,
            "name": c.name,
            "code": c.code,
            "instructor": c.instructor
        }
        for c in classroom.courses
    ]
    
    # Get recent announcements
    announcements = [
        {
            "id": a.id,
            "title": a.title,
            "content": a.content,
            "priority": a.priority,
            "created_at": a.created_at.isoformat()
        }
        for a in classroom.announcements[:10]
    ]
    
    return ClassroomHub(
        id=classroom.id,
        name=classroom.name,
        code=classroom.code,
        description=classroom.description,
        branch=classroom.branch,
        year_level=classroom.year_level,
        semester=classroom.semester,
        section=classroom.section,
        max_students=classroom.max_students,
        created_by=classroom.created_by,
        created_at=classroom.created_at,
        student_count=len(members),
        members=members,
        courses=courses,
        announcements=announcements
    )


@router.get("/list/by-branch", response_model=List[ClassroomResponse])
async def list_classrooms_by_branch(
    branch: Optional[str] = None,
    year_level: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List classrooms filtered by branch and year"""
    query = db.query(Classroom)
    
    # Enforce filtering based on user profile if set
    if current_user.year_level:
        query = query.filter(Classroom.year_level == current_user.year_level)
    elif year_level: # Fallback if user hasn't set it (should prompt them)
        query = query.filter(Classroom.year_level == year_level)
        
    if current_user.branch:
        query = query.filter(Classroom.branch == current_user.branch)
    elif branch:
        query = query.filter(Classroom.branch == branch)
        
    if current_user.section:
        query = query.filter(Classroom.section == current_user.section)
    
    classrooms = query.all()
    result = []
    for c in classrooms:
        student_count = db.query(ClassroomEnrollment).filter(
            ClassroomEnrollment.classroom_id == c.id
        ).count()
        result.append(ClassroomResponse(
            id=c.id,
            name=c.name,
            code=c.code,
            description=c.description,
            branch=c.branch,
            year_level=c.year_level,
            semester=c.semester,
            section=c.section,
            max_students=c.max_students,
            created_by=c.created_by,
            created_at=c.created_at,
            student_count=student_count
        ))
    return result


@router.post("/{classroom_id}/enroll", response_model=EnrollmentResponse)
async def enroll_in_classroom(
    classroom_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enroll current user in a classroom"""
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    # Check if already enrolled
    # Check if already enrolled in ANY classroom (Role=student)
    # Allows instructors to be in multiple? Maybe just students restricted?
    # User said: "allow him to see only that year classroom and let him pick his classroom once picked cannot be changed"
    
    # Check if user is enrolled in ANY classroom
    existing_any = db.query(ClassroomEnrollment).filter(
        ClassroomEnrollment.user_id == current_user.id
    ).first()
    
    if existing_any:
        if existing_any.classroom_id == classroom_id:
             raise HTTPException(status_code=400, detail="Already enrolled in this classroom")
        else:
             raise HTTPException(status_code=400, detail="You are already enrolled in a classroom. Cannot change without admin permission.")
    
    # Check capacity
    current_count = db.query(ClassroomEnrollment).filter(
        ClassroomEnrollment.classroom_id == classroom_id
    ).count()
    if current_count >= classroom.max_students:
        raise HTTPException(status_code=400, detail="Classroom is full")
    
    enrollment = ClassroomEnrollment(
        classroom_id=classroom_id,
        user_id=current_user.id,
        role="student"
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    
    return enrollment


@router.post("/{classroom_id}/study-group", response_model=StudyGroupResponse)
async def create_study_group(
    classroom_id: int,
    group_data: StudyGroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a study group in a classroom"""
    # Verify enrollment
    enrollment = db.query(ClassroomEnrollment).filter(
        ClassroomEnrollment.classroom_id == classroom_id,
        ClassroomEnrollment.user_id == current_user.id
    ).first()
    if not enrollment:
        raise HTTPException(status_code=403, detail="Not enrolled in this classroom")
    
    group = StudyGroup(
        classroom_id=classroom_id,
        name=group_data.name,
        topic=group_data.topic,
        leader_id=current_user.id,
        max_members=group_data.max_members
    )
    db.add(group)
    db.commit()
    db.refresh(group)
    
    # Add creator as member
    member = StudyGroupMember(
        group_id=group.id,
        user_id=current_user.id
    )
    db.add(member)
    db.commit()
    
    return StudyGroupResponse(
        id=group.id,
        classroom_id=group.classroom_id,
        name=group.name,
        topic=group.topic,
        leader_id=group.leader_id,
        max_members=group.max_members,
        member_count=1,
        created_at=group.created_at
    )
