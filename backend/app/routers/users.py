"""Users Router"""
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User, GitHubRepo, LinkedInExperience
from app.models.career import UserSkill
from app.schemas.user import UserResponse, UserUpdate, UserProfile, SkillCreate, SkillResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/profile/me", response_model=UserProfile)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's full profile"""
    # Get GitHub repos
    repos = db.query(GitHubRepo).filter(GitHubRepo.user_id == current_user.id).all()
    repos_data = [
        {
            "id": r.id,
            "repo_name": r.repo_name,
            "url": r.url,
            "description": r.description,
            "stars": r.stars,
            "language": r.language
        }
        for r in repos
    ]
    
    # Get LinkedIn experiences
    experiences = db.query(LinkedInExperience).filter(
        LinkedInExperience.user_id == current_user.id
    ).all()
    exp_data = [
        {
            "id": e.id,
            "company": e.company,
            "title": e.title,
            "start_date": e.start_date.isoformat() if e.start_date else None,
            "end_date": e.end_date.isoformat() if e.end_date else None
        }
        for e in experiences
    ]
    
    # Get enrollments
    enrollments_data = [
        {
            "classroom_id": e.classroom_id,
            "role": e.role,
            "classroom_name": e.classroom.name if e.classroom else None
        }
        for e in current_user.enrollments
    ]
    
    # Parse skills
    skills = json.loads(current_user.skills) if current_user.skills else []
    
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        student_id=current_user.student_id,
        phone=current_user.phone,
        gpa=current_user.gpa,
        github_url=current_user.github_url,
        linkedin_url=current_user.linkedin_url,
        profile_image=current_user.profile_image,
        bio=current_user.bio,
        year_level=current_user.year_level,
        branch=current_user.branch,
        section=current_user.section,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at,
        skills=skills,
        enrollments=enrollments_data,
        github_repos=repos_data,
        linkedin_experiences=exp_data
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    skills = json.loads(user.skills) if user.skills else []
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        student_id=user.student_id,
        phone=user.phone,
        gpa=user.gpa,
        github_url=user.github_url,
        linkedin_url=user.linkedin_url,
        profile_image=user.profile_image,
        bio=user.bio,
        year_level=user.year_level,
        branch=user.branch,
        section=user.section,
        is_admin=user.is_admin,
        created_at=user.created_at,
        skills=skills
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    update_data = user_data.model_dump(exclude_unset=True)
    
    # Prevent changing academic fields once set
    immutable_fields = ['branch', 'year_level', 'section']
    for field in immutable_fields:
        if field in update_data:
            current_val = getattr(current_user, field)
            new_val = update_data[field]
            # If field is already set (not None/Empty) and new value is different
            if current_val and new_val and current_val != new_val:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Cannot change {field} once set. Contact admin for changes."
                )
            
    for key, value in update_data.items():
        setattr(current_user, key, value)
    
    db.commit()
    db.refresh(current_user)
    
    skills = json.loads(current_user.skills) if current_user.skills else []
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        student_id=current_user.student_id,
        phone=current_user.phone,
        gpa=current_user.gpa,
        github_url=current_user.github_url,
        linkedin_url=current_user.linkedin_url,
        profile_image=current_user.profile_image,
        bio=current_user.bio,
        year_level=current_user.year_level,
        branch=current_user.branch,
        section=current_user.section,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at,
        skills=skills
    )


@router.post("/{user_id}/skills", response_model=SkillResponse)
async def add_skill(
    user_id: int,
    skill_data: SkillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a skill to user profile"""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    skill = UserSkill(
        user_id=user_id,
        skill_name=skill_data.skill_name,
        proficiency=skill_data.proficiency,
        years_experience=skill_data.years_experience,
        source="manual"
    )
    db.add(skill)
    db.commit()
    db.refresh(skill)
    
    # Also update user's skills JSON
    skills = json.loads(current_user.skills) if current_user.skills else []
    if skill_data.skill_name not in skills:
        skills.append(skill_data.skill_name)
        current_user.skills = json.dumps(skills)
        db.commit()
    
    return skill


@router.get("/{user_id}/skills", response_model=List[SkillResponse])
async def get_user_skills(user_id: int, db: Session = Depends(get_db)):
    """Get user's skills"""
    skills = db.query(UserSkill).filter(UserSkill.user_id == user_id).all()
    return skills
