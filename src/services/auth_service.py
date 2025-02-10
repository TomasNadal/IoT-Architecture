from typing import Optional, Dict
from datetime import datetime, timedelta
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import Session
from src.domain.model import User, Role
from src.config import get_jwt_secret

class AuthService:
    def __init__(self, session: Session, jwt_secret: str = None):
        self.session = session
        self.jwt_secret = jwt_secret or get_jwt_secret()

    def register_user(self, user_data: Dict) -> User:
        """Register a new user"""
        user = User(
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            email=user_data["email"],
            password=user_data["password"],
            role=user_data["role"]
        )
        self.session.add(user)
        self.session.flush()
        return user

    def authenticate(self, email: str, password: str) -> Optional[str]:
        """Authenticate user and return JWT token"""
        user = self.session.query(User).filter_by(email=email).first()
        
        if user and user.check_password(password):
            token_data = {
                'user_id': user.id,
                'email': user.email,
                'role': user.role.name,
                'permissions': list(user.permissions),
                'exp': datetime.utcnow() + timedelta(days=1)
            }
            return jwt.encode(token_data, self.jwt_secret, algorithm='HS256')
        return None

    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token and return payload"""
        try:
            print(f"\nAttempting to verify token...")
            print(f"Token: {token[:20]}...")
            print(f"Secret used: {self.jwt_secret[:5]}...")
            
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            print(f"Token decoded successfully!")
            print(f"Payload: {payload}")
            return payload
            
        except jwt.ExpiredSignatureError as e:
            print(f"Token expired: {str(e)}")
            return None
        except jwt.InvalidTokenError as e:
            print(f"Invalid token error: {str(e)}")
            return None
        except Exception as e:
            print(f"Unexpected error during token verification: {str(e)}")
            return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.session.query(User).filter_by(email=email).first()

    def get_user_permissions(self, user_id: int) -> list:
        """Get user permissions"""
        user = self.session.query(User).get(user_id)
        if user:
            return list(user.permissions)
        return []