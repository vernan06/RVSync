from passlib.context import CryptContext
import bcrypt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

try:
    print(f"Bcrypt version: {bcrypt.__version__}")
    hash = pwd_context.hash("testpassword")
    print(f"Hash success: {hash}")
    verify = pwd_context.verify("testpassword", hash)
    print(f"Verify success: {verify}")
except Exception as e:
    print(f"Error: {e}")
