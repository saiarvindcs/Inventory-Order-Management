from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from app.core.security.oauth2 import get_current_user
from app.models.user import User


def require_roles(*allowed_roles: str) -> Callable[..., User]:
    """Allow access only to active users with at least one active allowed role."""
    normalized_allowed = {role.strip().casefold() for role in allowed_roles if role.strip()}
    if not normalized_allowed:
        raise ValueError("At least one role must be supplied")

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_roles = {
            role.name.strip().casefold()
            for role in current_user.roles
            if role.is_active
        }
        if not user_roles.intersection(normalized_allowed):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )
        return current_user

    return role_checker


def require_permissions(*required_permissions: str) -> Callable[..., User]:
    """Require every named permission through the user's active roles."""
    normalized_required = {
        permission.strip().casefold()
        for permission in required_permissions
        if permission.strip()
    }
    if not normalized_required:
        raise ValueError("At least one permission must be supplied")

    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        granted = {
            permission.name.strip().casefold()
            for role in current_user.roles
            if role.is_active
            for permission in role.permissions
            if permission.is_active
        }
        if not normalized_required.issubset(granted):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have the required permission",
            )
        return current_user

    return permission_checker
