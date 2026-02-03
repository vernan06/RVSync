"""Seed Materials for Real Courses"""
from app.database import SessionLocal
from app.models.course import Course, CourseMaterial
from app.models.user import User

def seed_materials():
    db = SessionLocal()
    try:
        courses = db.query(Course).all()
        admin = db.query(User).filter(User.is_admin == 1).first()
        
        if not admin: return

        for course in courses:
            # Add a syllabus
            m1 = CourseMaterial(
                course_id=course.id,
                title=f"{course.code} Syllabus & Plan",
                type="document",
                description=f"Official syllabus and lesson plan for {course.name}.",
                uploaded_by=admin.id
            )
            # Add a lecture note
            m2 = CourseMaterial(
                course_id=course.id,
                title="Lecture 01: Introduction",
                type="document",
                description="Introductory lecture notes and prerequisites.",
                uploaded_by=admin.id
            )
            db.add_all([m1, m2])
        
        db.commit()
        print("Materials seeded successfully.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_materials()
