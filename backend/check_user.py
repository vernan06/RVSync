from app.database import SessionLocal
from app.models.user import User
from app.models.classroom import Classroom

def check_user():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "vernan@rvce.edu.in").first()
        if not user:
            print("User Vernan not found")
            return
        
        print(f"User: {user.name}, ID: {user.id}")
        print(f"Enrollments: {len(user.enrollments)}")
        for e in user.enrollments:
            c = db.query(Classroom).filter(Classroom.id == e.classroom_id).first()
            print(f"- Classroom: {c.name} ({c.code}), ID: {c.id}, Role: {e.role}")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_user()
