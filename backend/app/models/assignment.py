"""Assignment and Submission Models"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class Assignment(Base):
    __tablename__ = "assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Grading
    points = Column(Float, default=100.0)
    passing_score = Column(Float, default=50.0)
    
    # Dates
    due_date = Column(DateTime, nullable=False)
    allow_late = Column(Boolean, default=True)
    late_penalty = Column(Float, default=10.0)  # % per day
    
    # Settings
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    course = relationship("Course", back_populates="assignments")
    submissions = relationship("Submission", back_populates="assignment")


class Submission(Base):
    __tablename__ = "submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Submission Data
    file_path = Column(String(500))
    text_content = Column(Text)
    url = Column(String(500))
    
    # Status
    submission_time = Column(DateTime, default=datetime.utcnow)
    is_late = Column(Boolean, default=False)
    
    # Grading
    grade = Column(Float)
    feedback = Column(Text)
    graded_by = Column(Integer, ForeignKey("users.id"))
    graded_at = Column(DateTime)
    
    # Relationships
    assignment = relationship("Assignment", back_populates="submissions")
    user = relationship("User", back_populates="submissions", foreign_keys=[user_id])


class Test(Base):
    __tablename__ = "tests"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Configuration
    total_points = Column(Float, default=100.0)
    passing_score = Column(Float, default=40.0)
    time_limit = Column(Integer, default=60)  # minutes
    max_attempts = Column(Integer, default=1)
    
    # Questions (JSON-serialized)
    questions = Column(Text, default="[]")
    
    # Settings
    is_published = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    course = relationship("Course", back_populates="tests")
    results = relationship("TestResult", back_populates="test")


class TestResult(Base):
    __tablename__ = "test_results"
    
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Results
    score = Column(Float, default=0.0)
    percentage = Column(Float, default=0.0)
    passed = Column(Boolean, default=False)
    attempt_number = Column(Integer, default=1)
    
    # Answers (JSON-serialized)
    answers = Column(Text, default="{}")
    
    # Timing
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    test = relationship("Test", back_populates="results")
    user = relationship("User", back_populates="test_results")
