"""Admin Router - Full access for administrators"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.classroom import Classroom, ClassroomEnrollment
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/admin", tags=["Admin"])


def require_admin(current_user: User = Depends(get_current_user)):
    """Dependency to require admin privileges"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user


@router.get("/stats")
async def get_admin_stats(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all system statistics - Admin only"""
    
    # Get all users
    users = db.query(User).all()
    users_data = [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "student_id": u.student_id,
            "branch": u.branch,
            "year_level": u.year_level,
            "section": u.section,
            "gpa": u.gpa,
            "is_admin": u.is_admin,
            "created_at": u.created_at.isoformat() if u.created_at else None
        }
        for u in users
    ]
    
    # Get all classrooms
    classrooms = db.query(Classroom).all()
    classrooms_data = []
    for c in classrooms:
        student_count = db.query(ClassroomEnrollment).filter(
            ClassroomEnrollment.classroom_id == c.id
        ).count()
        classrooms_data.append({
            "id": c.id,
            "name": c.name,
            "code": c.code,
            "branch": c.branch.value if c.branch else None,
            "year_level": c.year_level.value if c.year_level else None,
            "section": c.section,
            "student_count": student_count,
            "max_students": c.max_students
        })
    
    # Get all enrollments
    enrollments = db.query(ClassroomEnrollment).all()
    enrollments_data = []
    for e in enrollments:
        user = db.query(User).filter(User.id == e.user_id).first()
        classroom = db.query(Classroom).filter(Classroom.id == e.classroom_id).first()
        enrollments_data.append({
            "id": e.id,
            "user_id": e.user_id,
            "user_name": user.name if user else "Unknown",
            "classroom_id": e.classroom_id,
            "classroom_name": classroom.name if classroom else "Unknown",
            "role": e.role,
            "enrolled_at": e.enrolled_at.isoformat() if e.enrolled_at else None
        })
    
    return {
        "total_users": len(users),
        "total_classrooms": len(classrooms),
        "total_enrollments": len(enrollments),
        "users": users_data,
        "classrooms": classrooms_data,
        "enrollments": enrollments_data
    }


@router.put("/user/{user_id}/update")
async def admin_update_user(
    user_id: int,
    data: dict,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update any user's data - Admin only (bypasses immutable field restrictions)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Admin can update any field
    for key, value in data.items():
        if hasattr(user, key):
            setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    
    return {"message": f"User {user_id} updated successfully"}
