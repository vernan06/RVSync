import sqlite3
import os

def list_users():
    db_path = "rvsync.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM users")
    for row in cursor.fetchall():
        print(row)
    conn.close()

if __name__ == "__main__":
    list_users()
