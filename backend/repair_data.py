import sqlite3
import os

def repair_data():
    db_path = "rvsync.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Find Vernan with correct email
    email = 'vernanshikir.cs24@rvce.edu.in'
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    user_row = cursor.fetchone()
    if not user_row:
        print(f"Vernan not found with email {email}")
        return
    vernan_id = user_row[0]
    print(f"Vernan ID: {vernan_id}")
    
    # 2. Find CSE-2E classroom
    cursor.execute("SELECT id FROM classrooms WHERE code = 'CSE-2E'")
    class_row = cursor.fetchone()
    if not class_row:
        print("CSE-2E classroom not found")
        return
    cse_id = class_row[0]
    print(f"CSE-2E ID: {cse_id}")
    
    # 3. Clear all enrollments for Vernan
    cursor.execute("DELETE FROM classroom_enrollments WHERE user_id = ?", (vernan_id,))
    print(f"Cleared all enrollments for Vernan.")
    
    # 4. Enroll Vernan in CSE-2E
    cursor.execute("INSERT INTO classroom_enrollments (user_id, classroom_id, role) VALUES (?, ?, ?)", 
                   (vernan_id, cse_id, 'student'))
    print(f"Enrolled Vernan in CSE-2E.")
    
    # 5. Clear all courses for CSE-2E
    cursor.execute("DELETE FROM courses WHERE classroom_id = ?", (cse_id,))
    print(f"Cleared existing courses for CSE-2E.")
    
    # 6. Delete those mock courses CS301 etc from ANY classroom to be safe
    cursor.execute("DELETE FROM courses WHERE code IN ('CS301', 'CS401', 'CS501')")
    print(f"Deleted mock courses CS301, CS401, CS501.")

    # 7. Insert ACTUAL courses
    courses_data = [
        ("MAT231TC", "Linear Algebra and Probability Theory", "Dr. Suma N Manjunath (sumanm@rvce.edu.in)", 4),
        ("IS233AI", "Data Structure and Applications", "Dr. Deepamala N (deepamalan@rvce.edu.in)", 4),
        ("CS234AI", "Applied Digital Logic Design and Computer Organisation", "Dr. Mohana (mohana@rvce.edu.in)", 4),
        ("CS235AI", "Operating Systems", "Prof. Savithri Kulkarni (savitrikulkarni@rvce.edu.in)", 4),
        ("CS237DL", "Design Thinking Lab", "Dr. Badari Nath K / Dr. Srividya M S", 2),
        ("CS139AT", "Bridge Course: C Programming", "Dr. Praveena T (praveenat@rvce.edu.in)", 0),
        ("CV232AT", "Environment & Sustainability", "TBA", 2)
    ]
    
    for code, name, instructor, credits in courses_data:
        cursor.execute("""
            INSERT INTO courses (classroom_id, name, code, instructor, credits, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (cse_id, name, code, instructor, credits, f"Course on {name} for CSE-2E."))
    
    print(f"Inserted {len(courses_data)} real courses into CSE-2E.")
    
    conn.commit()
    conn.close()
    print("Repair complete!")

if __name__ == "__main__":
    repair_data()
