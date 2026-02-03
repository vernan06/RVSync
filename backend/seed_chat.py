"""Seed Chat Messages for RVSync"""
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models.chat import ChatMessage
from app.models.user import User

def seed_chat():
    db = SessionLocal()
    try:
        vernan = db.query(User).filter(User.id == 1).first()
        admin = db.query(User).filter(User.id == 2).first()
        
        if not vernan or not admin:
            print("Users not found!")
            return
            
        messages = [
            (vernan.id, admin.id, "Hello Admin, I have a question about the course materials."),
            (admin.id, vernan.id, "Hi Vernan! Sure, what do you need help with?"),
            (vernan.id, admin.id, "Is the Unit II syllabus updated?"),
            (admin.id, vernan.id, "Yes, it's already updated in the Courses section. Check the new Stream feature too!")
        ]
        
        now = datetime.utcnow()
        for i, (from_id, to_id, text) in enumerate(messages):
            msg = ChatMessage(
                from_user_id=from_id,
                to_user_id=to_id,
                message=text,
                created_at=now - timedelta(minutes=10-i)
            )
            db.add(msg)
            
        db.commit()
        print(f"Seeded {len(messages)} messages.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_chat()
