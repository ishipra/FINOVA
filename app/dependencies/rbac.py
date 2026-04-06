from fastapi import Depends, HTTPException, status
from app.models.user import User, RoleEnum
from app.dependencies.auth import get_current_user

def require_role(*roles: RoleEnum):
    async def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in roles]}"
            )
        return current_user
    return dependency

require_admin = require_role(RoleEnum.admin)
require_analyst_or_admin = require_role(RoleEnum.analyst, RoleEnum.admin)
require_any = require_role(RoleEnum.viewer, RoleEnum.analyst, RoleEnum.admin)