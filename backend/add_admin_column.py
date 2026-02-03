import sqlite3
import os

DB_FILE = "rvsync.db"

def add_admin_column():
    if not os.path.exists(DB_FILE):
        print("Database file not found.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0")
            print("Added column: is_admin")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("Column is_admin already exists.")
            else:
                raise e
                
        conn.commit()
        print("Database schema updated.")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_admin_column()
