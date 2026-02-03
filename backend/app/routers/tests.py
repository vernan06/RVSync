"""Tests Router"""
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.classroom import ClassroomEnrollment
from app.models.course import Course
from app.models.assignment import Test, TestResult
from app.schemas.assignment import (
    TestCreate, TestResponse, TestDetail,
    TestSubmit, TestResultResponse, TestResultDetail
)
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api", tags=["Tests"])


@router.post("/classroom/{classroom_id}/course/{course_id}/test/create", response_model=TestResponse)
async def create_test(
    classroom_id: int,
    course_id: int,
    test_data: TestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a test for a course"""
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
        raise HTTPException(status_code=403, detail="Only instructors can create tests")
    
    # Serialize questions to JSON
    questions_json = json.dumps([q.model_dump() for q in test_data.questions])
    
    test = Test(
        course_id=course_id,
        title=test_data.title,
        description=test_data.description,
        total_points=test_data.total_points,
        passing_score=test_data.passing_score,
        time_limit=test_data.time_limit,
        max_attempts=test_data.max_attempts,
        questions=questions_json,
        created_by=current_user.id
    )
    db.add(test)
    db.commit()
    db.refresh(test)
    
    return TestResponse(
        id=test.id,
        course_id=test.course_id,
        title=test.title,
        description=test.description,
        total_points=test.total_points,
        passing_score=test.passing_score,
        time_limit=test.time_limit,
        max_attempts=test.max_attempts,
        is_published=test.is_published,
        created_at=test.created_at,
        question_count=len(test_data.questions)
    )


@router.get("/test/{test_id}/details", response_model=TestDetail)
async def get_test_details(
    test_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get test details including questions"""
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    questions = json.loads(test.questions) if test.questions else []
    
    # For students, remove correct answers
    course = db.query(Course).filter(Course.id == test.course_id).first()
    enrollment = db.query(ClassroomEnrollment).filter(
        ClassroomEnrollment.classroom_id == course.classroom_id,
        ClassroomEnrollment.user_id == current_user.id
    ).first()
    
    is_instructor = enrollment and enrollment.role == "instructor"
    if not is_instructor:
        for q in questions:
            q.pop("correct_answer", None)
    
    return TestDetail(
        id=test.id,
        course_id=test.course_id,
        title=test.title,
        description=test.description,
        total_points=test.total_points,
        passing_score=test.passing_score,
        time_limit=test.time_limit,
        max_attempts=test.max_attempts,
        is_published=test.is_published,
        created_at=test.created_at,
        question_count=len(questions),
        questions=questions
    )


@router.put("/test/{test_id}/publish")
async def publish_test(
    test_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Publish a test to make it available to students"""
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    test.is_published = True
    db.commit()
    
    return {"message": "Test published successfully"}


@router.post("/test/{test_id}/submit", response_model=TestResultResponse)
async def submit_test(
    test_id: int,
    answers_data: TestSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit test answers and get results"""
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    if not test.is_published:
        raise HTTPException(status_code=400, detail="Test not available yet")
    
    # Check attempt count
    existing_attempts = db.query(TestResult).filter(
        TestResult.test_id == test_id,
        TestResult.user_id == current_user.id
    ).count()
    
    if existing_attempts >= test.max_attempts:
        raise HTTPException(status_code=400, detail="Maximum attempts reached")
    
    # Grade the test
    questions = json.loads(test.questions) if test.questions else []
    score = 0.0
    
    for i, q in enumerate(questions):
        user_answer = answers_data.answers.get(str(i))
        if user_answer and user_answer.lower() == q.get("correct_answer", "").lower():
            score += q.get("points", 0)
    
    percentage = (score / test.total_points * 100) if test.total_points > 0 else 0
    passed = percentage >= test.passing_score
    
    result = TestResult(
        test_id=test_id,
        user_id=current_user.id,
        score=score,
        percentage=percentage,
        passed=passed,
        attempt_number=existing_attempts + 1,
        answers=json.dumps(answers_data.answers),
        completed_at=datetime.utcnow()
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    
    return result


@router.get("/test-result/{user_id}/all", response_model=List[TestResultResponse])
async def get_user_test_results(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all test results for a user"""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    results = db.query(TestResult).filter(TestResult.user_id == user_id).all()
    return results
