"""Seed Demo Context for RV-Assistant"""
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models.event import Event
from app.models.assignment import Assignment
from app.models.classroom import Classroom
from app.models.user import User

def seed_context():
    db = SessionLocal()
    try:
        vernan = db.query(User).filter(User.id == 1).first()
        if not vernan:
            print("Vernan not found!")
            return
            
        # Tomorrow's date
        tomorrow = datetime.utcnow() + timedelta(days=1)
        tomorrow_midday = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
        
        # 1. Create a Seminar Event
        seminar = Event(
            title="GenAI Seminar: Future of Agentic Coding",
            description="A special session by Google DeepMind experts.",
            start_time=tomorrow_midday,
            end_time=tomorrow_midday + timedelta(hours=2),
            location="Main Auditorium (R.V. College)",
            created_by=vernan.id,
            event_type="seminar"
        )
        db.add(seminar)
        
        # 2. Find Math Classroom and add an Assignment
        math_course = db.get(Classroom, 1) # Assuming ID 1 is the main classroom
        if math_course:
            assignment = Assignment(
                course_id=1, # Mat231TC usually in course table, let's just use 1 for demo
                title="Linear Algebra: Unit I Problem Set",
                description="Solve problems on Page 45 of the handbook.",
                due_date=tomorrow_midday + timedelta(hours=6), # Due tomorrow evening
                created_by=1
            )
            db.add(assignment)
            
        db.commit()
        print("Seeded tomorrow's schedule and assignments.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_context()
