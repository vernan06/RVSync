"""Seed Course Updates for RVSync"""
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.models.classroom import Classroom
from app.models.course import Course, CourseUpdate, CourseMaterial
from app.models.assignment import Assignment, Test
from datetime import datetime

def seed_updates():
    db = SessionLocal()
    try:
        # Find Math Course
        math_course = db.query(Course).filter(Course.code == "MAT231TC").first()
        if not math_course:
            print("Math course (MAT231TC) not found!")
            return

        # Find Instructor (or just use the first instructor/admin)
        instructor = db.query(User).filter(User.name == math_course.instructor).first()
        if not instructor:
            # Fallback to any user if specific instructor not found in DB users table
            instructor = db.query(User).first()

        updates = [
            {
                "content": "Welcome to Linear Algebra! I've uploaded the Unit I notes. Please review the first 3 chapters of the reference book.",
                "type": "announcement",
                "title": "Welcome & Unit I Notes"
            },
            {
                "content": "REMINDER: Practice Test for Unit I (Rank-Nullity & Eigenvalues) is now live in the Math Hub. Try to finish it before Saturday.",
                "type": "alert",
                "title": "Practice Test Live"
            },
            {
                "content": "Great job on the initial submissions! Unit II: Vector Spaces starts on Monday. Review the prerequisite material.",
                "type": "update",
                "title": "Upcoming: Unit II"
            }
        ]

        for u in updates:
            db_update = CourseUpdate(
                course_id=math_course.id,
                user_id=instructor.id,
                content=u["content"],
                type=u["type"],
                title=u["title"]
            )
            db.add(db_update)
        
        db.commit()
        print(f"Seeded {len(updates)} updates for {math_course.code}")

    except Exception as e:
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_updates()
