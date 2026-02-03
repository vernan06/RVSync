"""Classroom and Course Schemas"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# Classroom Schemas
class ClassroomCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    branch: str = "CSE"
    year_level: str = "FIRST"
    semester: str = "ODD"
    section: str = "A"
    max_students: int = 60


class ClassroomResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    branch: str
    year_level: str
    semester: str
    section: str
    max_students: int
    created_by: int
    created_at: datetime
    student_count: int = 0
    
    class Config:
        from_attributes = True


class ClassroomHub(ClassroomResponse):
    members: List[dict] = []
    courses: List[dict] = []
    announcements: List[dict] = []


# Enrollment Schemas
class EnrollmentCreate(BaseModel):
    classroom_id: int
    role: str = "student"


class EnrollmentResponse(BaseModel):
    id: int
    classroom_id: int
    user_id: int
    role: str
    enrolled_at: datetime
    
    class Config:
        from_attributes = True


# Course Schemas
class CourseCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    instructor: Optional[str] = None
    credits: int = 3


class CourseResponse(BaseModel):
    id: int
    classroom_id: int
    name: str
    code: str
    description: Optional[str] = None
    instructor: Optional[str] = None
    credits: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class CourseDetail(CourseResponse):
    materials: List[dict] = []
    assignments: List[dict] = []
    tests: List[dict] = []
    updates: List[dict] = []


# Course Update Schemas
class CourseUpdateCreate(BaseModel):
    title: Optional[str] = None
    content: str
    type: str = "update"  # update, announcement, alert
    is_pinned: bool = False


class CourseUpdateResponse(BaseModel):
    id: int
    course_id: int
    user_id: int
    title: Optional[str] = None
    content: str
    type: str
    is_pinned: bool
    created_at: datetime
    author_name: Optional[str] = None
    
    class Config:
        from_attributes = True


# Material Schemas
class MaterialCreate(BaseModel):
    title: str
    type: str = "document"  # document, link, video
    url: Optional[str] = None
    description: Optional[str] = None


class MaterialResponse(BaseModel):
    id: int
    course_id: int
    title: str
    type: str
    url: Optional[str] = None
    file_path: Optional[str] = None
    description: Optional[str] = None
    download_count: int = 0
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


# Study Group Schemas
class StudyGroupCreate(BaseModel):
    name: str
    topic: Optional[str] = None
    max_members: int = 10


class StudyGroupResponse(BaseModel):
    id: int
    classroom_id: int
    name: str
    topic: Optional[str] = None
    leader_id: int
    max_members: int
    member_count: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True
