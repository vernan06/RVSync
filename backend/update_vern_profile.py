from app.database import SessionLocal
from app.models.user import User
from app.models.classroom import Classroom, ClassroomEnrollment, Branch, YearLevel
from app.models.course import Course, CourseMaterial
from app.models.assignment import Assignment, Submission, Test, TestResult
import app.models.chat
import app.models.career

def update_vern():
    db = SessionLocal()
    try:
        # 1. Find User
        # Searching by name 'Vernan' (case insensitive match if needed, but simple first)
        user = db.query(User).filter(User.name.ilike("%Vernan%")).first()
        
        if not user:
            print("User 'Vernan' not found!")
            # Fallback: List all users to see who is there
            users = db.query(User).all()
            print("Available users:", [u.name for u in users])
            return

        print(f"Found User: {user.name} (ID: {user.id})")
        print(f"Current Status: {user.year_level}, {user.branch}, Section {user.section}")

        # 2. Update Profile
        user.year_level = YearLevel.SECOND
        user.branch = Branch.CSE
        user.section = "E"
        
        db.add(user)
        print(f"Updated Profile to: {user.year_level}, {user.branch}, Section {user.section}")

        # 3. Enroll in Classroom CSE-2E
        target_class_code = "CSE-2E"
        classroom = db.query(Classroom).filter(Classroom.code == target_class_code).first()
        
        if not classroom:
            print(f"Classroom {target_class_code} not found! Please ensure it is seeded.")
        else:
            # Check enrollment
            enrollment = db.query(ClassroomEnrollment).filter(
                ClassroomEnrollment.user_id == user.id,
                ClassroomEnrollment.classroom_id == classroom.id
            ).first()
            
            if not enrollment:
                new_enrollment = ClassroomEnrollment(
                    user_id=user.id,
                    classroom_id=classroom.id,
                    role="student"
                )
                db.add(new_enrollment)
                print(f"Enrolled {user.name} into {target_class_code}")
            else:
                print(f"User is already enrolled in {target_class_code}")

        db.commit()
        print("Update Complete!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    update_vern()
