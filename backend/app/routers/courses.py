"""Courses Router"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.classroom import Classroom, ClassroomEnrollment
from app.models.course import Course, CourseMaterial, CourseUpdate
from app.schemas.classroom import (
    CourseCreate, CourseResponse, CourseDetail, 
    MaterialCreate, MaterialResponse,
    CourseUpdateCreate, CourseUpdateResponse
)
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/classroom", tags=["Courses"])


@router.post("/{classroom_id}/course/create", response_model=CourseResponse)
async def create_course(
    classroom_id: int,
    course_data: CourseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a course in a classroom"""
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    # Verify instructor role
    enrollment = db.query(ClassroomEnrollment).filter(
        ClassroomEnrollment.classroom_id == classroom_id,
        ClassroomEnrollment.user_id == current_user.id,
        ClassroomEnrollment.role == "instructor"
    ).first()
    if not enrollment:
        raise HTTPException(status_code=403, detail="Only instructors can create courses")
    
    course = Course(
        classroom_id=classroom_id,
        name=course_data.name,
        code=course_data.code,
        description=course_data.description,
        instructor=course_data.instructor or current_user.name,
        credits=course_data.credits
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    
    return course



@router.get("/courses/my", response_model=List[CourseResponse])
async def get_my_courses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all courses for the current user's enrolled classrooms"""
    courses = []
    for enrollment in current_user.enrollments:
        classroom_courses = db.query(Course).filter(Course.classroom_id == enrollment.classroom_id).all()
        courses.extend(classroom_courses)
    return courses


@router.get("/{classroom_id}/courses", response_model=List[CourseResponse])
async def list_classroom_courses(
    classroom_id: int,
    db: Session = Depends(get_db)
):
    """List all courses in a classroom"""
    courses = db.query(Course).filter(Course.classroom_id == classroom_id).all()
    return courses


@router.get("/course/{course_id}", response_model=CourseDetail)
async def get_course_detail(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get course details with materials, assignments, and tests"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    materials = [
        {
            "id": m.id,
            "title": m.title,
            "type": m.type,
            "url": m.url,
            "download_count": m.download_count
        }
        for m in course.materials
    ]
    
    assignments = [
        {
            "id": a.id,
            "title": a.title,
            "due_date": a.due_date.isoformat(),
            "points": a.points
        }
        for a in course.assignments
    ]
    
    tests = [
        {
            "id": t.id,
            "title": t.title,
            "total_points": t.total_points,
            "time_limit": t.time_limit,
            "is_published": t.is_published
        }
        for t in course.tests
    ]
    
    updates = [
        {
            "id": u.id,
            "title": u.title,
            "content": u.content,
            "type": u.type,
            "is_pinned": u.is_pinned,
            "created_at": u.created_at.isoformat(),
            "author_name": u.author.name if u.author else "Faculty"
        }
        for u in sorted(course.updates, key=lambda x: x.created_at, reverse=True)
    ]
    
    return CourseDetail(
        id=course.id,
        classroom_id=course.classroom_id,
        name=course.name,
        code=course.code,
        description=course.description,
        instructor=course.instructor,
        credits=course.credits,
        created_at=course.created_at,
        materials=materials,
        assignments=assignments,
        tests=tests,
        updates=updates
    )


@router.post("/course/{course_id}/update", response_model=CourseUpdateResponse)
async def post_course_update(
    course_id: int,
    update_data: CourseUpdateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Post an update/announcement to a course"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Verify instructor role in the classroom
    enrollment = db.query(ClassroomEnrollment).filter(
        ClassroomEnrollment.classroom_id == course.classroom_id,
        ClassroomEnrollment.user_id == current_user.id,
        ClassroomEnrollment.role == "instructor"
    ).first()
    
    if not enrollment:
        raise HTTPException(status_code=403, detail="Only instructors can post course updates")
    
    update = CourseUpdate(
        course_id=course_id,
        user_id=current_user.id,
        title=update_data.title,
        content=update_data.content,
        type=update_data.type,
        is_pinned=update_data.is_pinned
    )
    db.add(update)
    db.commit()
    db.refresh(update)
    
    # Add author name for response
    update.author_name = current_user.name
    return update


@router.post("/{classroom_id}/course/{course_id}/material/add", response_model=MaterialResponse)
async def add_course_material(
    classroom_id: int,
    course_id: int,
    material_data: MaterialCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add material to a course"""
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.classroom_id == classroom_id
    ).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Verify instructor role
    enrollment = db.query(ClassroomEnrollment).filter(
        ClassroomEnrollment.classroom_id == classroom_id,
        ClassroomEnrollment.user_id == current_user.id,
        ClassroomEnrollment.role == "instructor"
    ).first()
    if not enrollment:
        raise HTTPException(status_code=403, detail="Only instructors can add materials")
    
    material = CourseMaterial(
        course_id=course_id,
        title=material_data.title,
        type=material_data.type,
        url=material_data.url,
        description=material_data.description,
        uploaded_by=current_user.id
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    
    return material


@router.get("/course/{course_id}/materials", response_model=List[MaterialResponse])
async def get_course_materials(course_id: int, db: Session = Depends(get_db)):
    """Get all materials for a course"""
    materials = db.query(CourseMaterial).filter(
        CourseMaterial.course_id == course_id
    ).all()
    return materials


@router.post("/material/{material_id}/download")
async def track_material_download(material_id: int, db: Session = Depends(get_db)):
    """Increment download count for a material"""
    material = db.query(CourseMaterial).filter(CourseMaterial.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    material.download_count += 1
    db.commit()
    
    return {"message": "Download tracked", "url": material.url}
