import sys
import traceback
from app.database import SessionLocal
from app.models.event import Event
from app.models.user import User
from app.models.classroom import Classroom
from datetime import datetime, timedelta

def main():
    db = SessionLocal()
    try:
        print("Starting seeding...")
        admin = db.query(User).filter(User.is_admin == 1).first()
        if not admin:
            print("No admin found")
            return
            
        classroom = db.query(Classroom).filter(Classroom.code == "CSE-2E").first()
        cid = classroom.id if classroom else None
        
        now = datetime.utcnow()
        e = Event(
            title="Seminar: Future of AI",
            description="Insightful session on agentic AI.",
            location="Room F101",
            start_time=now + timedelta(hours=1),
            end_time=now + timedelta(hours=3),
            event_type="seminar",
            classroom_id=cid,
            created_by=admin.id
        )
        db.add(e)
        db.commit()
        print("Event seeded successfully")
    except Exception:
        print("SEEDING FAILED")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
