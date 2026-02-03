from app.database import SessionLocal
from app.models.user import User
import app.models.assignment
import app.models.career
import app.models.chat
import app.models.classroom
import app.models.course

def test_update():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == 1).first()
        if not user:
            print("User 1 missing")
            return

        print(f"Before: Branch={user.branch}, Year={user.year_level}, Section={user.section}")
        
        # Update
        user.branch = "CSE"
        user.year_level = "FIRST"
        user.section = "A"
        
        db.commit()
        db.refresh(user)
        
        print(f"After: Branch={user.branch}, Year={user.year_level}, Section={user.section}")
        
        if user.section == "A":
            print("SUCCESS: Section updated.")
        else:
            print("FAILURE: Section not updated.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_update()
