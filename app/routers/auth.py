from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.deps.auth import get_db, get_current_user
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserResponse
from app.auth.oauth import auth_service
from app.services.user import user_service
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login with username and password."""
    # Find user by email/username
    user = db.query(User).filter(User.email == request.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Verify password
    if not auth_service.verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    # Create access token
    access_token = auth_service.create_access_token(
        data={"sub": user.email, "user_id": user.id}
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user information."""
    return UserResponse.model_validate(current_user)


@router.get("/status")
async def auth_status(current_user: User = Depends(get_current_user)):
    """Check authentication status."""
    return {
        "authenticated": True,
        "user_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role
    }