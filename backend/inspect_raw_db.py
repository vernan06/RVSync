import sqlite3
import os

def inspect_db():
    db_path = "rvsync.db"
    if not os.path.exists(db_path):
        print(f"DB not found at {db_path}")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("--- CLASSROOMS ---")
    cursor.execute("SELECT id, name, code FROM classrooms")
    for row in cursor.fetchall():
        print(row)
        
    print("\n--- COURSES ---")
    cursor.execute("SELECT id, classroom_id, name, code, instructor FROM courses")
    for row in cursor.fetchall():
        print(row)
        
    print("\n--- USERS ---")
    cursor.execute("SELECT id, name, email FROM users")
    for row in cursor.fetchall():
        print(row)
        
    print("\n--- ENROLLMENTS ---")
    cursor.execute("SELECT user_id, classroom_id, role FROM classroom_enrollments")
    for row in cursor.fetchall():
        print(row)
        
    conn.close()

if __name__ == "__main__":
    inspect_db()
