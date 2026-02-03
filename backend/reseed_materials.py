import sqlite3
import os

def seed_materials():
    db_path = "rvsync.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all courses for CSE-2E (ID 10)
    cursor.execute("SELECT id, code FROM courses WHERE classroom_id = 10")
    courses = cursor.fetchall()
    
    for course_id, code in courses:
        # Add basic materials
        m1 = (course_id, f"{code} Syllabus", "document", "Official syllabus.", 1)
        m2 = (course_id, "Lecture Notes - Module 1", "document", "Foundations and intro.", 1)
        
        cursor.execute("""
            INSERT INTO course_materials (course_id, title, type, description, uploaded_by, uploaded_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, m1)
        cursor.execute("""
            INSERT INTO course_materials (course_id, title, type, description, uploaded_by, uploaded_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, m2)
        
    conn.commit()
    conn.close()
    print("Materials re-seeded successfully.")

if __name__ == "__main__":
    seed_materials()
