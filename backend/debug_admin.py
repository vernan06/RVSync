from app.database import SessionLocal
from app.models.user import User
import app.models.assignment
import app.models.career
import app.models.chat
import app.models.classroom
import app.models.course
from passlib.context import CryptContext

pwd = CryptContext(schemes=['bcrypt'])
db = SessionLocal()

# Check admin
admin = db.query(User).filter(User.email == 'admin@rvce.edu.in').first()
print(f"Admin exists: {admin is not None}")

if admin:
    print(f"Password hash: {admin.password_hash[:50]}...")
    print(f"Password valid: {pwd.verify('admin123', admin.password_hash)}")
    print(f"is_admin: {admin.is_admin}")
else:
    print("Creating admin user...")
    admin = User(
        email='admin@rvce.edu.in',
        password_hash=pwd.hash('admin123'),
        name='Administrator',
        is_admin=1
    )
    db.add(admin)
    db.commit()
    print(f"Created admin user ID: {admin.id}")

db.close()
