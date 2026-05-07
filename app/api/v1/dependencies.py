from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.tenant import User, UserRole
from app.repositories.tenants import get_tenant_by_code
from app.repositories.users import get_user_by_id
from app.services.auth import AuthError, decode_access_token


@dataclass(frozen=True)
class AuthContext:
    tenant_id: int
    user: User | None = None


def get_current_merchant_context(
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None, alias="Authorization"),
    merchant_code: str | None = Header(default=None, alias="X-Merchant-Code"),
) -> AuthContext:
    if authorization:
        return _context_from_bearer(db, authorization, merchant_code)
    if merchant_code:
        tenant = get_tenant_by_code(db, merchant_code)
        if tenant is None:
            raise HTTPException(status_code=400, detail="invalid merchant code")
        return AuthContext(tenant_id=tenant.id)
    raise HTTPException(status_code=401, detail="missing authorization")


def _context_from_bearer(db: Session, authorization: str, merchant_code: str | None) -> AuthContext:
    token_type, _, token = authorization.partition(" ")
    if token_type.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="invalid authorization header")
    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])
    except (AuthError, KeyError, TypeError, ValueError):
        raise HTTPException(status_code=401, detail="invalid access token") from None

    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="inactive user")

    if user.role == UserRole.super_admin:
        if not merchant_code:
            raise HTTPException(status_code=400, detail="super admin must provide X-Merchant-Code")
        tenant = get_tenant_by_code(db, merchant_code)
        if tenant is None:
            raise HTTPException(status_code=400, detail="invalid merchant code")
        return AuthContext(tenant_id=tenant.id, user=user)

    if user.role != UserRole.merchant_admin or user.tenant_id is None:
        raise HTTPException(status_code=403, detail="insufficient role")
    return AuthContext(tenant_id=user.tenant_id, user=user)
