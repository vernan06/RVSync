"""User Model"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    student_id = Column(String(50), unique=True, index=True)
    phone = Column(String(20))
    
    # Academic Info
    gpa = Column(Float, default=0.0)
    enrollment_date = Column(DateTime, default=datetime.utcnow)
    year_level = Column(String(20))
    branch = Column(String(50))
    section = Column(String(10))
    is_admin = Column(Integer, default=0)  # 0 = False, 1 = True
    
    # Profile Links
    github_url = Column(String(255))
    linkedin_url = Column(String(255))
    profile_image = Column(String(255))
    bio = Column(Text)
    
    # Skills (JSON-serialized list)
    skills = Column(Text, default="[]")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    classrooms_created = relationship("Classroom", back_populates="creator")
    enrollments = relationship("ClassroomEnrollment", back_populates="user")
    submissions = relationship("Submission", foreign_keys="Submission.user_id", back_populates="user")
    test_results = relationship("TestResult", back_populates="user")
    messages_sent = relationship("ChatMessage", foreign_keys="ChatMessage.from_user_id", back_populates="sender")
    messages_received = relationship("ChatMessage", foreign_keys="ChatMessage.to_user_id", back_populates="receiver")
    announcements = relationship("Announcement", back_populates="author")
    github_repos = relationship("GitHubRepo", back_populates="user")
    linkedin_experiences = relationship("LinkedInExperience", back_populates="user")
    events_created = relationship("Event", back_populates="creator")


class GitHubRepo(Base):
    __tablename__ = "github_repos"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    repo_name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    description = Column(Text)
    stars = Column(Integer, default=0)
    forks = Column(Integer, default=0)
    language = Column(String(100))
    topics = Column(Text)  # JSON list
    last_updated = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="github_repos", foreign_keys=[user_id])


class LinkedInExperience(Base):
    __tablename__ = "linkedin_experiences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    location = Column(String(255))
    start_date = Column(DateTime)
    end_date = Column(DateTime)  # NULL = current
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="linkedin_experiences", foreign_keys=[user_id])
