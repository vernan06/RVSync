"""Assignment, Test, and Submission Schemas"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Any


# Assignment Schemas
class AssignmentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    points: float = 100.0
    due_date: datetime
    allow_late: bool = True
    late_penalty: float = 10.0


class AssignmentResponse(BaseModel):
    id: int
    course_id: int
    title: str
    description: Optional[str] = None
    points: float
    due_date: datetime
    allow_late: bool
    created_at: datetime
    submission_count: int = 0
    
    class Config:
        from_attributes = True


# Submission Schemas
class SubmissionCreate(BaseModel):
    text_content: Optional[str] = None
    url: Optional[str] = None


class SubmissionResponse(BaseModel):
    id: int
    assignment_id: int
    user_id: int
    file_path: Optional[str] = None
    text_content: Optional[str] = None
    url: Optional[str] = None
    submission_time: datetime
    is_late: bool
    grade: Optional[float] = None
    feedback: Optional[str] = None
    graded_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class GradeSubmission(BaseModel):
    grade: float
    feedback: Optional[str] = None


# Test Schemas
class QuestionCreate(BaseModel):
    question: str
    type: str = "mcq"  # mcq, short_answer
    options: List[str] = []
    correct_answer: str
    points: float = 10.0


class TestCreate(BaseModel):
    title: str
    description: Optional[str] = None
    total_points: float = 100.0
    passing_score: float = 40.0
    time_limit: int = 60
    max_attempts: int = 1
    questions: List[QuestionCreate] = []


class TestResponse(BaseModel):
    id: int
    course_id: int
    title: str
    description: Optional[str] = None
    total_points: float
    passing_score: float
    time_limit: int
    max_attempts: int
    is_published: bool
    created_at: datetime
    question_count: int = 0
    
    class Config:
        from_attributes = True


class TestDetail(TestResponse):
    questions: List[dict] = []


# Test Result Schemas
class TestSubmit(BaseModel):
    answers: dict  # {question_index: answer}


class TestResultResponse(BaseModel):
    id: int
    test_id: int
    user_id: int
    score: float
    percentage: float
    passed: bool
    attempt_number: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TestResultDetail(TestResultResponse):
    answers: dict = {}
    correct_answers: dict = {}
