from app.routers.auth import verify_password, create_access_token
from app.schemas.user import Token
from app.config import get_settings

def test_components():
    print("Testing Auth Components...")
    
    # Test verify_password
    print("1. Verify Password")
    try:
        # Mock hash
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed = pwd_context.hash("admin123")
        
        valid = verify_password("admin123", hashed)
        print(f"Password Valid: {valid}")
    except Exception as e:
        print(f"Verify Password Failed: {e}")

    # Test create_access_token
    print("\n2. Create Token")
    try:
        token = create_access_token({"sub": "1"})
        print(f"Token created: {token[:10]}...")
    except Exception as e:
        print(f"Create Token Failed: {e}")

    # Test Token Schema instantiation
    print("\n3. Token Schema")
    try:
        t = Token(
            access_token="test_token",
            user_id=1,
            name="Test User"
            # Omitting token_type to test default
        )
        print(f"Token instantiated: {t}")
    except Exception as e:
        print(f"Token Validation Failed: {e}")

if __name__ == "__main__":
    test_components()
