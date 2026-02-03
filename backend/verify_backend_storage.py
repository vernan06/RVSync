from app.database import SessionLocal, engine
from app.models.user import User
from sqlalchemy import text
import sys

def verify_storage():
    print("--- Verifying Database Schema ---")
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(users)"))
        columns = [row[1] for row in result]
        print(f"Columns in 'users' table: {columns}")
        
        required = ['branch', 'year_level', 'section']
        missing = [col for col in required if col not in columns]
        if missing:
            print(f"CRITICAL: Missing columns in DB: {missing}")
            return
        else:
            print("All required columns exist in DB.")

    print("\n--- Testing Model Update ---")
    db = SessionLocal()
    try:
        # Get user 1
        user = db.query(User).filter(User.id == 1).first()
        if not user:
            print("User 1 not found. Creating dummy user.")
            user = User(email="test@test.com", password_hash="hash", name="Test User")
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created User {user.id}")
        
        print(f"Current Data - Branch: {user.branch}, Year: {user.year_level}, Section: {user.section}")
        
        # Simulating Update (resetting first to test clean save)
        # Force clear them first (manually) to test "First time set" behavior
        user.branch = None
        user.year_level = None
        user.section = None
        db.commit()
        print("Cleared fields for testing.")
        
        # Set values
        print("Setting Branch='CSE', Year='FIRST', Section='A'")
        user.branch = "CSE"
        user.year_level = "FIRST"
        user.section = "A"
        db.commit()
        
        # refresh
        db.refresh(user)
        print(f"After Update - Branch: {user.branch}, Year: {user.year_level}, Section: {user.section}")
        
        if user.branch == "CSE" and user.section == "A":
            print("SUCCESS: Data persisted correctly.")
        else:
            print("FAILURE: Data did NOT persist.")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify_storage()
