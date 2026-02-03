from app.database import SessionLocal
from app.models.course import Course
from app.models.classroom import Classroom

def list_courses():
    db = SessionLocal()
    try:
        classrooms = db.query(Classroom).all()
        for cl in classrooms:
            print(f"Classroom: {cl.name} ({cl.code}), ID: {cl.id}")
            courses = db.query(Course).filter(Course.classroom_id == cl.id).all()
            for c in courses:
                print(f"  - Course: {c.name} ({c.code}), Instructor: {c.instructor}")
        
        # Check for courses with no classroom
        orphan_courses = db.query(Course).filter(Course.classroom_id == None).all()
        if orphan_courses:
            print("Orphan Courses (No Classroom):")
            for c in orphan_courses:
                print(f"  - Course: {c.name} ({c.code})")
    finally:
        db.close()

if __name__ == "__main__":
    list_courses()
