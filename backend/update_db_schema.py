import sqlite3
import os

DB_FILE = "rvsync.db"

def add_columns():
    if not os.path.exists(DB_FILE):
        print("Database file not found.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Add year_level
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN year_level VARCHAR(20)")
            print("Added column: year_level")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("Column year_level already exists.")
            else:
                raise e
        
        # Add branch
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN branch VARCHAR(50)")
            print("Added column: branch")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("Column branch already exists.")
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
    add_columns()
