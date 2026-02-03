import sys
import os
from sqlalchemy import create_engine, text
from passlib.context import CryptContext
import bcrypt

# Add app to path
sys.path.append(os.getcwd())

def verify():
    print("--- Verifying Reversion ---")
    
    # 1. Check Bcrypt Version
    print(f"Bcrypt Version: {bcrypt.__version__}")
    
    # 2. Check Database
    try:
        engine = create_engine("sqlite:///./rvsync.db")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, email, is_admin FROM users WHERE email='admin@rvce.edu.in'"))
            admin = result.fetchone()
            if admin:
                print(f"✅ Admin found in DB: {admin}")
            else:
                print("❌ Admin NOT found in DB")
    except Exception as e:
        print(f"❌ Database Error: {e}")

    # 3. Check Auth Logic Import
    try:
        from app.routers import auth
        print("✅ Auth Router imported successfully (No storage dependency)")
    except ImportError as e:
        print(f"❌ Import Error in Auth: {e}")
        
    # 4. Check User Schema
    try:
        from app.schemas.user import UserBase
        print("✅ User Schema imported")
    except Exception as e:
        print(f"❌ User Schema Error: {e}")

if __name__ == "__main__":
    verify()
