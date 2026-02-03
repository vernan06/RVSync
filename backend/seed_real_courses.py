"""Seed Real Courses with Faculty Emails"""
from app.database import SessionLocal
from app.models.classroom import Classroom
from app.models.course import Course
from app.models.user import User

def seed_real_courses():
    db = SessionLocal()
    try:
        classroom = db.query(Classroom).filter(Classroom.code == "CSE-2E").first()
        if not classroom: return

        # Delete old ones
        db.query(Course).filter(Course.classroom_id == classroom.id).delete()
        db.commit()

        courses_data = [
            {
                "code": "MAT231TC",
                "name": "Linear Algebra and Probability Theory",
                "instructor": "Dr. Suma N Manjunath (sumanm@rvce.edu.in)",
                "credits": 4
            },
            {
                "code": "IS233AI",
                "name": "Data Structure and Applications",
                "instructor": "Dr. Deepamala N (deepamalan@rvce.edu.in)",
                "credits": 4
            },
            {
                "code": "CS234AI",
                "name": "Applied Digital Logic Design and Computer Organisation",
                "instructor": "Dr. Mohana (mohana@rvce.edu.in)",
                "credits": 4
            },
            {
                "code": "CS235AI",
                "name": "Operating Systems",
                "instructor": "Prof. Savithri Kulkarni (savitrikulkarni@rvce.edu.in)",
                "credits": 4
            },
            {
                "code": "CS237DL",
                "name": "Design Thinking Lab",
                "instructor": "Dr. Badari Nath K (badarinath.kb@rvce.edu.in) / Dr. Srividya M S (srividyams@rvce.edu.in)",
                "credits": 2
            },
            {
                "code": "CS139AT",
                "name": "Bridge Course: C Programming",
                "instructor": "Dr. Praveena T (praveenat@rvce.edu.in)",
                "credits": 0
            },
            {
                "code": "CV232AT",
                "name": "Environment & Sustainability",
                "instructor": "TBA",
                "credits": 2
            }
        ]

        for c_data in courses_data:
            course = Course(
                classroom_id=classroom.id,
                name=c_data["name"],
                code=c_data["code"],
                instructor=c_data["instructor"],
                credits=c_data["credits"],
                description=f"Course on {c_data['name']} for {classroom.name}."
            )
            db.add(course)
        
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    seed_real_courses()
