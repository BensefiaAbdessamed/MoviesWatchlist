from datetime import UTC, datetime, timedelta
from fastapi import Depends, HTTPException, status
import jwt

from typing import Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.engine.result import result_tuple
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.user import Token
from app.core.config import settings
from app.models.database import Role, User

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")



def hash_password(password: str):
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return password_hash.verify(plain_password, hashed_password)

def create_access_token(
    data: dict, 
    expire_delta: Optional[timedelta] = None
):
    data_copy = data.copy()

    if expire_delta:
        expire = expire_delta + datetime.now(UTC)
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)

    data_copy.update({"exp": expire})
    encoded_jwt = jwt.encode(data_copy, settings.secret_key.get_secret_value(), algorithm=settings.algorithm)
    return encoded_jwt

def verify_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm],
            options={"require": ["exp", "sub"]},
        )

    except jwt.InvalidTokenError:
        return None
    else:
        sub = payload.get("sub")
        return int(sub) if sub else None

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    token_data = verify_access_token(token=token)
    

    result = await db.execute(select(User).where(User.id == token_data)) if token_data else None
    user = result.scalar_one_or_none() if result else None
    
    if user is None:
        raise credentials_exception
        
    return user

def get_current_user_id(
    current_user: User = Depends(get_current_user),
):
    return current_user.id

class RoleChecker:
    def __init__(self, allowed_roles: list[Role]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)):

        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action."
            )
        return current_user