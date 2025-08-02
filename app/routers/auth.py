from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.deps.auth import get_db, get_current_user
from app.schemas.auth import GoogleTokenRequest, TokenResponse
from app.schemas.user import UserResponse
from app.auth.oauth import auth_service
from app.services.user import user_service
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=TokenResponse)
async def login_with_google(
    request: GoogleTokenRequest,
    db: Session = Depends(get_db)
):
    """Login with Google OAuth token."""
    # Verify Google token
    try:
        google_user_info = auth_service.verify_google_token(request.google_token)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Token verification failed: {str(e)}"
        )

    email = google_user_info.get("email")
    name = google_user_info.get("name", email)

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not found in Google token"
        )

    # Get or create user
    user = user_service.get_user_by_email(db, email)
    if not user:
        user = user_service.create_user_from_oauth(db, email, name)

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