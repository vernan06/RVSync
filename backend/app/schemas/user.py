"""User Schemas"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


# Auth Schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    student_id: Optional[str] = None
    phone: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str
    year_level: Optional[str] = None
    branch: Optional[str] = None
    section: Optional[str] = None
    is_admin: int = 0


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    gpa: Optional[float] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    profile_image: Optional[str] = None
    bio: Optional[str] = None
    year_level: Optional[str] = None
    branch: Optional[str] = None
    section: Optional[str] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime
    skills: List[str] = []
    
    class Config:
        from_attributes = True


class UserProfile(UserResponse):
    enrollments: List[dict] = []
    github_repos: List[dict] = []
    linkedin_experiences: List[dict] = []


# GitHub Schemas
class GitHubRepoResponse(BaseModel):
    id: int
    repo_name: str
    url: str
    description: Optional[str] = None
    stars: int = 0
    forks: int = 0
    language: Optional[str] = None
    topics: List[str] = []
    
    class Config:
        from_attributes = True


# LinkedIn Schemas
class LinkedInExperienceResponse(BaseModel):
    id: int
    company: str
    title: str
    location: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    description: Optional[str] = None
    
    class Config:
        from_attributes = True


# Skill Schemas
class SkillCreate(BaseModel):
    skill_name: str
    proficiency: str = "intermediate"
    years_experience: float = 0.0


class SkillResponse(BaseModel):
    id: int
    skill_name: str
    proficiency: str
    years_experience: float
    endorsed_count: int = 0
    source: Optional[str] = None
    
    class Config:
        from_attributes = True
