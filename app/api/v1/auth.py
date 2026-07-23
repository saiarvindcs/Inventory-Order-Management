from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token_type,
)
from app.core.security.oauth2 import get_current_user
from app.core.security.rbac import require_roles
from app.db.session import get_db
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
)
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserResponse
from app.services.user import UserService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
) -> UserResponse:
    try:
        created_user = UserService.register_user(
            db=db,
            user_data=user,
        )

        return UserResponse.model_validate(created_user)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    try:
        user = UserService.authenticate_user(
            db=db,
            email=str(credentials.email),
            password=credentials.password,
        )

        access_token = create_access_token(
            subject=str(user.id),
            additional_claims={
                "email": user.email,
            },
        )

        refresh_token = create_refresh_token(
            subject=str(user.id),
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
def refresh_access_token(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    payload = decode_token(token_data.refresh_token)

    if payload is None or not verify_token_type(
        payload,
        expected_type="refresh",
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    subject = payload.get("sub")

    if not isinstance(subject, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(subject)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token subject",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user = UserRepository.get_by_id(db=db, user_id=user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is unavailable",
            headers={"WWW-Authenticate": "Bearer"},
        )

    new_access_token = create_access_token(
        subject=subject,
    )

    new_refresh_token = create_refresh_token(
        subject=subject,
    )

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.get(
    "/admin-only",
)
def admin_only(
    current_user: User = Depends(
        require_roles("Admin"),
    ),
) -> dict[str, str]:
    return {
        "message": (
            f"Welcome Admin, "
            f"{current_user.full_name}!"
        )
    }