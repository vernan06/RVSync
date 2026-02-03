"""Career Intelligence Schemas"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# Opportunity Schemas
class OpportunityCreate(BaseModel):
    title: str
    company: str
    description: Optional[str] = None
    location: Optional[str] = None
    job_type: str = "full-time"
    required_skills: List[str] = []
    nice_to_have: List[str] = []
    min_experience: int = 0
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    external_url: Optional[str] = None


class OpportunityResponse(BaseModel):
    id: int
    title: str
    company: str
    description: Optional[str] = None
    location: Optional[str] = None
    job_type: str
    required_skills: List[str] = []
    nice_to_have: List[str] = []
    min_experience: int
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    posted_at: datetime
    
    class Config:
        from_attributes = True


# Match Schemas
class OpportunityMatchResponse(BaseModel):
    opportunity: OpportunityResponse
    overall_score: float
    skill_match_score: float
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    is_hidden_gem: bool = False
    
    class Config:
        from_attributes = True


# Career Prediction Schemas
class CareerPredictionResponse(BaseModel):
    predicted_role: str
    timeline_months: int
    confidence: float
    alternative_roles: List[str] = []
    insights: Optional[str] = None
    recommendations: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Dashboard Schemas
class DashboardMetrics(BaseModel):
    gpa: float = 0.0
    assignments_completed: int = 0
    total_assignments: int = 0
    completion_percentage: float = 0.0
    skills_count: int = 0
    projects_count: int = 0
    opportunity_matches: int = 0
    unread_messages: int = 0
    upcoming_deadlines: List[dict] = []


class AcademicProgress(BaseModel):
    course_grades: List[dict] = []
    assignment_scores: List[dict] = []
    test_scores: List[dict] = []
    gpa_trend: List[dict] = []


class SkillAnalytics(BaseModel):
    skills: List[dict] = []
    skill_growth: List[dict] = []
    skill_distribution: dict = {}
    top_skills: List[str] = []
