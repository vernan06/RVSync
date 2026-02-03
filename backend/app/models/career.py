"""Career Intelligence Models"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Boolean
from app.database import Base


class Opportunity(Base):
    __tablename__ = "opportunities"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    description = Column(Text)
    location = Column(String(255))
    job_type = Column(String(50), default="full-time")  # full-time, part-time, internship, contract
    
    # Requirements
    required_skills = Column(Text, default="[]")  # JSON list
    nice_to_have = Column(Text, default="[]")  # JSON list
    min_experience = Column(Integer, default=0)  # years
    
    # Compensation
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    currency = Column(String(10), default="INR")
    
    # Metadata
    source = Column(String(100))  # LinkedIn, Naukri, etc.
    external_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    posted_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
    # ML-generated fields
    embedding = Column(Text)  # JSON list of 384 floats




class OpportunityMatch(Base):
    __tablename__ = "opportunity_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"), nullable=False)
    
    # Match Scores
    overall_score = Column(Float, default=0.0)  # 0-100
    skill_match_score = Column(Float, default=0.0)
    experience_match_score = Column(Float, default=0.0)
    
    # Analysis
    matched_skills = Column(Text, default="[]")  # JSON list
    missing_skills = Column(Text, default="[]")  # JSON list
    is_hidden_gem = Column(Boolean, default=False)  # Anomaly detection flag
    
    # Timestamps
    calculated_at = Column(DateTime, default=datetime.utcnow)


class CareerPrediction(Base):
    __tablename__ = "career_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Predictions
    predicted_role = Column(String(255))
    timeline_months = Column(Integer)  # 6-36
    confidence = Column(Float)  # 0-100
    
    # Alternative paths
    alternative_roles = Column(Text, default="[]")  # JSON list
    
    # Feature values used
    features = Column(Text, default="{}")  # JSON object
    
    # Insights from LLM
    insights = Column(Text)
    recommendations = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)


class UserSkill(Base):
    __tablename__ = "user_skills"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    skill_name = Column(String(100), nullable=False)
    proficiency = Column(String(20), default="intermediate")  # beginner, intermediate, advanced, expert
    years_experience = Column(Float, default=0.0)
    endorsed_count = Column(Integer, default=0)
    source = Column(String(50))  # manual, github, linkedin
    created_at = Column(DateTime, default=datetime.utcnow)
