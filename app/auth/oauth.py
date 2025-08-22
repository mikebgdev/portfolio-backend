from passlib.context import CryptContext


class AuthService:
    """Simple password hashing service for SQLAdmin authentication"""

    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)

    def hash_password(self, password: str) -> str:
        """Generate password hash."""
        return self.pwd_context.hash(password)


# Global auth service instance
auth_service = AuthService()
