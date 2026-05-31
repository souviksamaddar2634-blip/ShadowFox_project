from fastapi import Depends, HTTPException, status
from typing import Any, Dict, List

from utils.auth import get_current_user
from utils.logger import logger

def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Dependency to verify that the authenticated user is currently active."""
    if not current_user.get("is_active", True):
        logger.warning(f"Auth failure: Inactive user '{current_user.get('username')}' attempted access.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your user account is inactive. Please contact system administrators.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user

def require_admin(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
    """Dependency to assert that the active authenticated user has the 'admin' role."""
    if current_user.get("role") != "admin":
        logger.warning(
            f"Admin authorization failure: User '{current_user.get('username')}' (role: '{current_user.get('role')}') "
            f"attempted to access an admin-restricted endpoint."
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Insufficient permissions (Admin role required)."
        )
    return current_user

def require_roles(*allowed_roles: str):
    """Dependency factory for validating multiple allowed roles for authorization checks."""
    def role_dependency(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
        if current_user.get("role") not in allowed_roles:
            logger.warning(
                f"Role authorization failure: User '{current_user.get('username')}' (role: '{current_user.get('role')}') "
                f"denied access to resource requiring roles: {allowed_roles}."
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Insufficient permissions (requires one of: {allowed_roles})."
            )
        return current_user
    return role_dependency
