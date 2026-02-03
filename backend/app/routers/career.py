"""Career Intelligence Router"""
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import httpx

from app.database import get_db
from app.config import get_settings
from app.models.user import User, GitHubRepo
from app.models.career import Opportunity, OpportunityMatch, CareerPrediction, UserSkill
from app.schemas.career import (
    OpportunityResponse, OpportunityMatchResponse,
    CareerPredictionResponse, DashboardMetrics, AcademicProgress
)
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api", tags=["Career Intelligence"])
settings = get_settings()


@router.post("/sync/github/{user_id}")
async def sync_github(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync GitHub repositories for a user"""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if not current_user.github_url:
        raise HTTPException(status_code=400, detail="GitHub URL not set")
    
    # Extract username from URL
    github_url = current_user.github_url.rstrip("/")
    username = github_url.split("/")[-1]
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.GITHUB_API_URL}/users/{username}/repos",
                headers={"Accept": "application/vnd.github.v3+json"},
                params={"sort": "updated", "per_page": 30}
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to fetch GitHub repos")
            
            repos = response.json()
            
            # Clear existing repos
            db.query(GitHubRepo).filter(GitHubRepo.user_id == user_id).delete()
            
            # Add new repos
            skills_found = set()
            for repo in repos:
                github_repo = GitHubRepo(
                    user_id=user_id,
                    repo_name=repo["name"],
                    url=repo["html_url"],
                    description=repo.get("description"),
                    stars=repo.get("stargazers_count", 0),
                    forks=repo.get("forks_count", 0),
                    language=repo.get("language"),
                    topics=json.dumps(repo.get("topics", [])),
                    last_updated=datetime.fromisoformat(repo["updated_at"].replace("Z", "+00:00")) if repo.get("updated_at") else None
                )
                db.add(github_repo)
                
                # Extract skills from language
                if repo.get("language"):
                    skills_found.add(repo["language"])
                
                # Extract from topics
                for topic in repo.get("topics", []):
                    skills_found.add(topic)
            
            # Update user skills
            for skill_name in skills_found:
                existing = db.query(UserSkill).filter(
                    UserSkill.user_id == user_id,
                    UserSkill.skill_name == skill_name
                ).first()
                if not existing:
                    skill = UserSkill(
                        user_id=user_id,
                        skill_name=skill_name,
                        source="github"
                    )
                    db.add(skill)
            
            # Update user's skills JSON
            current_skills = json.loads(current_user.skills) if current_user.skills else []
            all_skills = list(set(current_skills) | skills_found)
            current_user.skills = json.dumps(all_skills)
            
            db.commit()
            
            return {
                "message": f"Synced {len(repos)} repositories",
                "skills_found": list(skills_found)
            }
    except httpx.RequestError:
        raise HTTPException(status_code=500, detail="Failed to connect to GitHub API")


@router.get("/opportunities/match/{user_id}", response_model=List[OpportunityMatchResponse])
async def get_opportunity_matches(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get matched opportunities for a user"""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get user skills
    user_skills = db.query(UserSkill).filter(UserSkill.user_id == user_id).all()
    skill_names = set(s.skill_name.lower() for s in user_skills)
    
    # Get all active opportunities
    opportunities = db.query(Opportunity).filter(Opportunity.is_active == True).all()
    
    matches = []
    for opp in opportunities:
        required = json.loads(opp.required_skills) if opp.required_skills else []
        nice_to_have = json.loads(opp.nice_to_have) if opp.nice_to_have else []
        
        required_lower = [s.lower() for s in required]
        nice_lower = [s.lower() for s in nice_to_have]
        
        # Calculate match scores
        matched_skills = [s for s in required if s.lower() in skill_names]
        matched_nice = [s for s in nice_to_have if s.lower() in skill_names]
        missing_skills = [s for s in required if s.lower() not in skill_names]
        
        required_match = len(matched_skills) / len(required) * 100 if required else 100
        nice_match = len(matched_nice) / len(nice_to_have) * 50 if nice_to_have else 0
        
        overall_score = min(required_match + nice_match * 0.3, 100)
        
        # Determine if it's a "hidden gem" using simple heuristics
        is_hidden_gem = (
            overall_score >= 60 and
            overall_score < 85 and
            len(matched_skills) >= 2 and
            opp.salary_max and opp.salary_max > 1500000
        )
        
        matches.append(OpportunityMatchResponse(
            opportunity=OpportunityResponse(
                id=opp.id,
                title=opp.title,
                company=opp.company,
                description=opp.description,
                location=opp.location,
                job_type=opp.job_type,
                required_skills=required,
                nice_to_have=nice_to_have,
                min_experience=opp.min_experience,
                salary_min=opp.salary_min,
                salary_max=opp.salary_max,
                posted_at=opp.posted_at
            ),
            overall_score=round(overall_score, 1),
            skill_match_score=round(required_match, 1),
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            is_hidden_gem=is_hidden_gem
        ))
    
    # Sort by score
    matches.sort(key=lambda x: x.overall_score, reverse=True)
    return matches[:20]


@router.get("/predict-career/{user_id}", response_model=CareerPredictionResponse)
async def predict_career(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get career prediction for a user"""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get user data
    skills = db.query(UserSkill).filter(UserSkill.user_id == user_id).all()
    repos = db.query(GitHubRepo).filter(GitHubRepo.user_id == user_id).all()
    
    skill_count = len(skills)
    project_count = len(repos)
    
    # Simple prediction logic (would be ML model in production)
    if skill_count >= 10 and project_count >= 15:
        predicted_role = "Senior Software Engineer"
        timeline = 12
        confidence = 85.0
        alternatives = ["Tech Lead", "Staff Engineer", "Engineering Manager"]
    elif skill_count >= 5 and project_count >= 8:
        predicted_role = "Software Engineer II"
        timeline = 6
        confidence = 78.0
        alternatives = ["Full Stack Developer", "Backend Engineer", "DevOps Engineer"]
    elif skill_count >= 3:
        predicted_role = "Junior Developer"
        timeline = 3
        confidence = 90.0
        alternatives = ["Software Engineer I", "Associate Developer", "Graduate Engineer"]
    else:
        predicted_role = "Intern/Entry Level"
        timeline = 6
        confidence = 70.0
        alternatives = ["SDE Intern", "Trainee Developer", "Fresher Developer"]
    
    # Generate insights
    insights = f"""
Based on your {skill_count} skills and {project_count} projects, you're well-positioned for {predicted_role} roles.
Your GitHub activity shows strong engagement with open source.
Focus on deepening expertise in your top skills to accelerate career growth.
    """.strip()
    
    recommendations = """
1. Continue building projects to demonstrate practical skills
2. Consider obtaining cloud certifications (AWS/GCP)
3. Contribute to open source projects for visibility
4. Network with professionals in your target role
    """.strip()
    
    # Save prediction
    prediction = CareerPrediction(
        user_id=user_id,
        predicted_role=predicted_role,
        timeline_months=timeline,
        confidence=confidence,
        alternative_roles=json.dumps(alternatives),
        insights=insights,
        recommendations=recommendations,
        features=json.dumps({
            "skill_count": skill_count,
            "project_count": project_count,
            "gpa": current_user.gpa
        })
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    
    return CareerPredictionResponse(
        predicted_role=predicted_role,
        timeline_months=timeline,
        confidence=confidence,
        alternative_roles=alternatives,
        insights=insights,
        recommendations=recommendations,
        created_at=prediction.created_at
    )


@router.get("/dashboard/metrics/{user_id}", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard metrics for a user"""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    from app.models.assignment import Submission, Assignment
    from app.models.chat import ChatMessage
    from app.models.classroom import ClassroomEnrollment
    
    # Count skills
    skills = db.query(UserSkill).filter(UserSkill.user_id == user_id).count()
    
    # Count projects (repos)
    projects = db.query(GitHubRepo).filter(GitHubRepo.user_id == user_id).count()
    
    # Get enrollments
    enrollments = db.query(ClassroomEnrollment).filter(
        ClassroomEnrollment.user_id == user_id
    ).all()
    classroom_ids = [e.classroom_id for e in enrollments]
    
    # Count assignments
    from app.models.course import Course
    courses = db.query(Course).filter(Course.classroom_id.in_(classroom_ids)).all()
    course_ids = [c.id for c in courses]
    
    total_assignments = db.query(Assignment).filter(
        Assignment.course_id.in_(course_ids)
    ).count()
    
    completed_assignments = db.query(Submission).filter(
        Submission.user_id == user_id,
        Submission.grade != None
    ).count()
    
    # Unread messages
    unread = db.query(ChatMessage).filter(
        ChatMessage.to_user_id == user_id,
        ChatMessage.is_read == False
    ).count()
    
    # Upcoming deadlines
    upcoming = db.query(Assignment).filter(
        Assignment.course_id.in_(course_ids),
        Assignment.due_date > datetime.utcnow()
    ).order_by(Assignment.due_date).limit(5).all()
    
    completion_pct = (completed_assignments / total_assignments * 100) if total_assignments > 0 else 0
    
    return DashboardMetrics(
        gpa=current_user.gpa or 0.0,
        assignments_completed=completed_assignments,
        total_assignments=total_assignments,
        completion_percentage=round(completion_pct, 1),
        skills_count=skills,
        projects_count=projects,
        opportunity_matches=0,  # Would calculate from matches
        unread_messages=unread,
        upcoming_deadlines=[
            {
                "id": a.id,
                "title": a.title,
                "due_date": a.due_date.isoformat(),
                "points": a.points
            }
            for a in upcoming
        ]
    )
