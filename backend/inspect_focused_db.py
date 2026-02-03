import sqlite3
import os

def inspect_db():
    db_path = "rvsync.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("--- CLASSROOMS (ID, Name, Code) ---")
    cursor.execute("SELECT id, name, code FROM classrooms")
    classrooms = cursor.fetchall()
    for row in classrooms:
        print(row)
        
    print("\n--- COURSES (ID, ClassroomID, Name, Code) ---")
    cursor.execute("SELECT id, classroom_id, name, code FROM courses")
    for row in cursor.fetchall():
        print(row)
        
    print("\n--- VERNAN'S ENROLLMENTS (User ID 1) ---")
    cursor.execute("SELECT classroom_id, role FROM classroom_enrollments WHERE user_id = 1")
    for row in cursor.fetchall():
        print(row)
        
    conn.close()

if __name__ == "__main__":
    inspect_db()
