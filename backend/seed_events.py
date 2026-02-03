"""Seed Events for RVSync"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models.event import Event
from app.models.user import User
from app.models.classroom import Classroom

def seed_events():
    db = SessionLocal()
    try:
        # Get admin user
        admin = db.query(User).filter(User.is_admin == 1).first()
        if not admin:
            print("Admin user not found. Please run register_admin.py first.")
            return

        # Get CSE-2E classroom
        classroom = db.query(Classroom).filter(Classroom.code == "CSE-2E").first()
        if not classroom:
            print("CSE-2E classroom not found. Skipping classroom events.")
            classroom_id = None
        else:
            classroom_id = classroom.id

        now = datetime.utcnow()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        events = [
            # Global Events
            {
                "title": "Republic Day Celebration",
                "description": "Annual flag hoisting ceremony at the main ground.",
                "location": "Main Ground",
                "start_time": today + timedelta(days=2, hours=9),
                "end_time": today + timedelta(days=2, hours=12),
                "is_all_day": False,
                "event_type": "activity",
                "classroom_id": None
            },
            {
                "title": "Placement Orientation",
                "description": "Orientation session for final year placements.",
                "location": "Auditorium",
                "start_time": today + timedelta(days=5, hours=14),
                "end_time": today + timedelta(days=5, hours=16),
                "is_all_day": False,
                "event_type": "seminar",
                "classroom_id": None
            },
            # Classroom Specific (Today)
            {
                "title": "Mini Project Review - I",
                "description": "First phase review for the Operating Systems mini project.",
                "location": "Room F101",
                "start_time": today + timedelta(hours=14, minutes=30),
                "end_time": today + timedelta(hours=16, minutes=30),
                "is_all_day": False,
                "event_type": "exam",
                "classroom_id": classroom_id
            },
            {
                "title": "Guest Lecture on IoT",
                "description": "Special lecture by industry expert from Intel.",
                "location": "Online (Teams)",
                "start_time": today + timedelta(hours=10),
                "end_time": today + timedelta(hours=11, minutes=30),
                "is_all_day": False,
                "event_type": "seminar",
                "classroom_id": classroom_id
            },
            # Future Classroom Events
            {
                "title": "Data Structures Workshop",
                "description": "Hands-on session on advanced graph algorithms.",
                "location": "Lab 5",
                "start_time": today + timedelta(days=1, hours=10),
                "end_time": today + timedelta(days=1, hours=13),
                "is_all_day": False,
                "event_type": "activity",
                "classroom_id": classroom_id
            }
        ]

        for event_data in events:
            event = Event(
                **event_data,
                created_by=admin.id
            )
            db.add(event)
        
        db.commit()
        print(f"Successfully seeded {len(events)} events!")

    except Exception as e:
        print(f"Error seeding events: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_events()
