"""Assignments Router"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.classroom import ClassroomEnrollment
from app.models.course import Course
from app.models.assignment import Assignment, Submission
from app.schemas.assignment import (
    AssignmentCreate, AssignmentResponse,
    SubmissionCreate, SubmissionResponse, GradeSubmission
)
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/classroom", tags=["Assignments"])


@router.post("/{classroom_id}/course/{course_id}/assignment/create", response_model=AssignmentResponse)
async def create_assignment(
    classroom_id: int,
    course_id: int,
    assignment_data: AssignmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create an assignment for a course"""
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.classroom_id == classroom_id
    ).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Verify instructor role
    enrollment = db.query(ClassroomEnrollment).filter(
        ClassroomEnrollment.classroom_id == classroom_id,
        ClassroomEnrollment.user_id == current_user.id,
        ClassroomEnrollment.role == "instructor"
    ).first()
    if not enrollment:
        raise HTTPException(status_code=403, detail="Only instructors can create assignments")
    
    assignment = Assignment(
        course_id=course_id,
        title=assignment_data.title,
        description=assignment_data.description,
        points=assignment_data.points,
        due_date=assignment_data.due_date,
        allow_late=assignment_data.allow_late,
        late_penalty=assignment_data.late_penalty,
        created_by=current_user.id
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    
    return AssignmentResponse(
        id=assignment.id,
        course_id=assignment.course_id,
        title=assignment.title,
        description=assignment.description,
        points=assignment.points,
        due_date=assignment.due_date,
        allow_late=assignment.allow_late,
        created_at=assignment.created_at,
        submission_count=0
    )


@router.get("/assignment/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(assignment_id: int, db: Session = Depends(get_db)):
    """Get assignment details"""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    submission_count = db.query(Submission).filter(
        Submission.assignment_id == assignment_id
    ).count()
    
    return AssignmentResponse(
        id=assignment.id,
        course_id=assignment.course_id,
        title=assignment.title,
        description=assignment.description,
        points=assignment.points,
        due_date=assignment.due_date,
        allow_late=assignment.allow_late,
        created_at=assignment.created_at,
        submission_count=submission_count
    )


@router.post("/submission/{assignment_id}/submit", response_model=SubmissionResponse)
async def submit_assignment(
    assignment_id: int,
    submission_data: SubmissionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit an assignment"""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Check for existing submission
    existing = db.query(Submission).filter(
        Submission.assignment_id == assignment_id,
        Submission.user_id == current_user.id
    ).first()
    if existing:
        # Update existing submission
        existing.text_content = submission_data.text_content
        existing.url = submission_data.url
        existing.submission_time = datetime.utcnow()
        existing.is_late = datetime.utcnow() > assignment.due_date
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new submission
    is_late = datetime.utcnow() > assignment.due_date
    if is_late and not assignment.allow_late:
        raise HTTPException(status_code=400, detail="Late submissions not allowed")
    
    submission = Submission(
        assignment_id=assignment_id,
        user_id=current_user.id,
        text_content=submission_data.text_content,
        url=submission_data.url,
        is_late=is_late
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    
    return submission


@router.get("/submission/{assignment_id}/my", response_model=SubmissionResponse)
async def get_my_submission(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's submission for an assignment"""
    submission = db.query(Submission).filter(
        Submission.assignment_id == assignment_id,
        Submission.user_id == current_user.id
    ).first()
    if not submission:
        raise HTTPException(status_code=404, detail="No submission found")
    return submission


@router.get("/assignment/{assignment_id}/submissions", response_model=List[SubmissionResponse])
async def list_assignment_submissions(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all submissions for an assignment (instructor only)"""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Get course and verify instructor role
    course = db.query(Course).filter(Course.id == assignment.course_id).first()
    enrollment = db.query(ClassroomEnrollment).filter(
        ClassroomEnrollment.classroom_id == course.classroom_id,
        ClassroomEnrollment.user_id == current_user.id,
        ClassroomEnrollment.role == "instructor"
    ).first()
    if not enrollment:
        raise HTTPException(status_code=403, detail="Only instructors can view all submissions")
    
    submissions = db.query(Submission).filter(
        Submission.assignment_id == assignment_id
    ).all()
    return submissions


@router.put("/submission/{submission_id}/grade", response_model=SubmissionResponse)
async def grade_submission(
    submission_id: int,
    grade_data: GradeSubmission,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Grade a submission"""
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Verify instructor role
    assignment = db.query(Assignment).filter(Assignment.id == submission.assignment_id).first()
    course = db.query(Course).filter(Course.id == assignment.course_id).first()
    enrollment = db.query(ClassroomEnrollment).filter(
        ClassroomEnrollment.classroom_id == course.classroom_id,
        ClassroomEnrollment.user_id == current_user.id,
        ClassroomEnrollment.role == "instructor"
    ).first()
    if not enrollment:
        raise HTTPException(status_code=403, detail="Only instructors can grade submissions")
    
    # Apply late penalty if applicable
    grade = grade_data.grade
    if submission.is_late and assignment.late_penalty > 0:
        # Calculate days late
        days_late = (submission.submission_time - assignment.due_date).days + 1
        penalty = min(days_late * assignment.late_penalty, 50)  # Max 50% penalty
        grade = grade * (1 - penalty / 100)
    
    submission.grade = grade
    submission.feedback = grade_data.feedback
    submission.graded_by = current_user.id
    submission.graded_at = datetime.utcnow()
    db.commit()
    db.refresh(submission)
    
    return submission
