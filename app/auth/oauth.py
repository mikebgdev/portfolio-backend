from fastapi import HTTPException, status
from google.auth.transport import requests
from google.oauth2 import id_token
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.config import settings


class AuthService:
    def verify_google_token(self, token: str) -> Dict[str, Any]:
        """Verify Google OAuth token and return user info."""
        try:
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), settings.google_client_id
            )
            
            # Verify the token is for our application
            if idinfo['aud'] != settings.google_client_id:
                raise ValueError('Wrong audience')
                
            return idinfo
            
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Google token: {str(e)}"
            )

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
            
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.secret_key, 
            algorithm=settings.algorithm
        )
        return encoded_jwt

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(
                token, 
                settings.secret_key, 
                algorithms=[settings.algorithm]
            )
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )


# Global auth service instance
auth_service = AuthService()