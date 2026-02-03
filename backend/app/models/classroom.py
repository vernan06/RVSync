"""Classroom Models"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class Branch(str, enum.Enum):
    CSE = "CSE"
    ECE = "ECE"
    EEE = "EEE"
    MECH = "MECH"
    CIVIL = "CIVIL"
    ISE = "ISE"
    AIML = "AIML"
    OTHER = "OTHER"


class YearLevel(str, enum.Enum):
    FIRST = "FIRST"
    SECOND = "SECOND"
    THIRD = "THIRD"
    FOURTH = "FOURTH"


class Semester(str, enum.Enum):
    ODD = "ODD"
    EVEN = "EVEN"


class Classroom(Base):
    __tablename__ = "classrooms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(500))
    
    # Classification
    branch = Column(String(50), default="CSE")
    year_level = Column(String(20), default="FIRST")
    semester = Column(String(10), default="ODD")
    section = Column(String(10), default="A")
    
    # Settings
    max_students = Column(Integer, default=60)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", back_populates="classrooms_created")
    enrollments = relationship("ClassroomEnrollment", back_populates="classroom")
    courses = relationship("Course", back_populates="classroom")
    announcements = relationship("Announcement", back_populates="classroom")
    study_groups = relationship("StudyGroup", back_populates="classroom")
    events = relationship("Event", back_populates="classroom")


class ClassroomEnrollment(Base):
    __tablename__ = "classroom_enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(20), default="student")  # student, instructor, ta
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    classroom = relationship("Classroom", back_populates="enrollments")
    user = relationship("User", back_populates="enrollments")


class StudyGroup(Base):
    __tablename__ = "study_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False)
    name = Column(String(255), nullable=False)
    topic = Column(String(500))
    leader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    max_members = Column(Integer, default=10)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    classroom = relationship("Classroom", back_populates="study_groups")
    members = relationship("StudyGroupMember", back_populates="group")


class StudyGroupMember(Base):
    __tablename__ = "study_group_members"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("study_groups.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    group = relationship("StudyGroup", back_populates="members")
