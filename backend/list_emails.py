import sqlite3
import os

def list_emails():
    db_path = "rvsync.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM users")
    for row in cursor.fetchall():
        print(row[0])
    conn.close()

if __name__ == "__main__":
    list_emails()
