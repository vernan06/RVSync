import sqlite3
import os

DB_FILE = "rvsync.db"

def add_section_column():
    if not os.path.exists(DB_FILE):
        print("Database file not found.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Add section
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN section VARCHAR(10)")
            print("Added column: section")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("Column section already exists.")
            else:
                raise e
                
        conn.commit()
        print("Database schema updated successfully.")
        
    except Exception as e:
        print(f"Error updating schema: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_section_column()
