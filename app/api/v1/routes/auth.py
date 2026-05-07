from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.users import get_user_by_username
from app.schemas.auth import LoginRequest, LoginResponse
from app.services.auth import create_access_token, verify_password

router = APIRouter(prefix="/auth")


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    user = get_user_by_username(db, payload.username)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="invalid username or password")
    token = create_access_token(str(user.id), user.role.value, user.tenant_id)
    return LoginResponse(access_token=token, role=user.role.value, tenant_id=user.tenant_id)
