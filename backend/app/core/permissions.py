"""RBAC Permission system."""

from enum import Enum
from functools import wraps
from fastapi import HTTPException, status, Depends
from app.core.security import get_current_active_user


class Role(str, Enum):
    ADMIN = "admin"
    DIRECTOR = "director"
    MANAGER = "manager"
    WAREHOUSE = "warehouse"
    PRODUCTION = "production"
    ENGINEERING = "engineering"
    MAINTENANCE = "maintenance"
    PURCHASING = "purchasing"
    QA = "qa"


class Permission(str, Enum):
    VIEW = "view"
    CREATE = "create"
    EDIT = "edit"
    DELETE = "delete"
    APPROVE = "approve"
    PRINT = "print"
    EXPORT_EXCEL = "export_excel"
    IMPORT_EXCEL = "import_excel"


# Permission matrix: role -> set of permissions
ROLE_PERMISSIONS: dict[str, set[str]] = {
    Role.ADMIN: {
        Permission.VIEW, Permission.CREATE, Permission.EDIT, Permission.DELETE,
        Permission.APPROVE, Permission.PRINT, Permission.EXPORT_EXCEL, Permission.IMPORT_EXCEL,
    },
    Role.DIRECTOR: {
        Permission.VIEW, Permission.APPROVE, Permission.PRINT, Permission.EXPORT_EXCEL,
    },
    Role.MANAGER: {
        Permission.VIEW, Permission.CREATE, Permission.EDIT,
        Permission.APPROVE, Permission.PRINT, Permission.EXPORT_EXCEL,
    },
    Role.WAREHOUSE: {
        Permission.VIEW, Permission.CREATE, Permission.EDIT,
        Permission.PRINT, Permission.EXPORT_EXCEL, Permission.IMPORT_EXCEL,
    },
    Role.PRODUCTION: {
        Permission.VIEW, Permission.CREATE,
        Permission.PRINT, Permission.EXPORT_EXCEL,
    },
    Role.ENGINEERING: {
        Permission.VIEW, Permission.CREATE,
        Permission.PRINT, Permission.EXPORT_EXCEL,
    },
    Role.MAINTENANCE: {
        Permission.VIEW, Permission.CREATE,
        Permission.PRINT, Permission.EXPORT_EXCEL,
    },
    Role.PURCHASING: {
        Permission.VIEW, Permission.CREATE, Permission.EDIT,
        Permission.PRINT, Permission.EXPORT_EXCEL,
    },
    Role.QA: {
        Permission.VIEW,
        Permission.PRINT, Permission.EXPORT_EXCEL,
    },
}


def has_permission(role: str, permission: str) -> bool:
    """Check if a role has a specific permission."""
    role_perms = ROLE_PERMISSIONS.get(role, set())
    return permission in role_perms


def require_permission(*permissions: str):
    """FastAPI dependency that checks user has required permission(s)."""
    async def permission_checker(current_user=Depends(get_current_active_user)):
        user_perms = ROLE_PERMISSIONS.get(current_user.role, set())
        for perm in permissions:
            if perm not in user_perms:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {perm} required",
                )
        return current_user
    return permission_checker


def require_roles(*roles: str):
    """FastAPI dependency that checks user has one of the required roles."""
    async def role_checker(current_user=Depends(get_current_active_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {current_user.role} not authorized. Required: {', '.join(roles)}",
            )
        return current_user
    return role_checker
