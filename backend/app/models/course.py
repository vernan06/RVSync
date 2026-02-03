"""Course and Material Models"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False)
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False)
    description = Column(Text)
    instructor = Column(String(255))
    credits = Column(Integer, default=3)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    classroom = relationship("Classroom", back_populates="courses")
    materials = relationship("CourseMaterial", back_populates="course")
    assignments = relationship("Assignment", back_populates="course")
    tests = relationship("Test", back_populates="course")
    updates = relationship("CourseUpdate", back_populates="course")


class CourseMaterial(Base):
    __tablename__ = "course_materials"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String(255), nullable=False)
    type = Column(String(50), default="document")  # document, link, video
    url = Column(String(500))
    file_path = Column(String(500))
    description = Column(Text)
    
    # Tracking
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    download_count = Column(Integer, default=0)
    
    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    course = relationship("Course", back_populates="materials")


class CourseUpdate(Base):
    __tablename__ = "course_updates"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Content
    content = Column(Text, nullable=False)
    title = Column(String(255))
    type = Column(String(20), default="update")  # update, announcement, alert
    
    # Metadata
    is_pinned = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    course = relationship("Course", back_populates="updates")
    author = relationship("User")
