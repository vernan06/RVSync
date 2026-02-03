from app.database import SessionLocal
from app.models.classroom import Classroom, Branch, YearLevel, Semester
from app.models.user import User
# Import other models to ensure relationships resolve
import app.models.assignment
import app.models.chat
import app.models.career
import app.models.course
from sqlalchemy.orm import Session
import sys

def seed_cse_classrooms():
    db = SessionLocal()
    try:
        # Get a default user for creator (ID 1)
        creator = db.query(User).filter(User.id == 1).first()
        if not creator:
            print("Error: User with ID 1 not found. Please register a user first.")
            return

        print(f"Creating classrooms with creator: {creator.name} (ID: {creator.id})")
        
        branch = Branch.CSE
        sections = ['A', 'B', 'C', 'D', 'E']
        years = [
            (YearLevel.FIRST, Semester.ODD),   # 1st Year
            (YearLevel.SECOND, Semester.ODD),  # 2nd Year (assuming ODD sem currently)
            (YearLevel.THIRD, Semester.ODD),   # 3rd Year
            (YearLevel.FOURTH, Semester.ODD)   # 4th Year
        ]
        
        count = 0
        for year, semester in years:
            for section in sections:
                # Generate unique code like CSE-1A-2026, CSE-3C-2026
                # Or simpler: CSE-1A
                # Using Year number map
                year_num_map = {
                    YearLevel.FIRST: 1,
                    YearLevel.SECOND: 2,
                    YearLevel.THIRD: 3,
                    YearLevel.FOURTH: 4
                }
                year_num = year_num_map[year]
                
                class_name = f"CSE {year_num}{section}"
                class_code = f"CSE-{year_num}{section}"
                
                # Check if exists
                existing = db.query(Classroom).filter(Classroom.code == class_code).first()
                if existing:
                    print(f"Skipping {class_code} (already exists)")
                    continue
                
                classroom = Classroom(
                    name=f"Computer Science - {year_num} Year, Section {section}",
                    code=class_code,
                    description=f"{year.value} Year CSE Classroom, Section {section}",
                    branch=branch,
                    year_level=year,
                    semester=semester,
                    section=section,
                    max_students=70,
                    created_by=creator.id
                )
                db.add(classroom)
                count += 1
        
        db.commit()
        print(f"Successfully created {count} CSE classrooms!")
        
    except Exception as e:
        print(f"Error seeding data: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_cse_classrooms()
