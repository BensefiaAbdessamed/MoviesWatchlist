from sqlite3 import IntegrityError
from sqlalchemy import select

from fastapi import APIRouter, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.core.auth import create_access_token, hash_password, verify_password
from app.database.session import get_db
from app.models.database import User
from app.schemas import user
from app.core import auth

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()

    #   validate user cridentials
    if not user:
        raise HTTPException(status_code=401, detail="user not found")

    valid = verify_password(form_data.password, user.password_hash)
    if not valid:
        raise HTTPException(status_code=401, detail="username or password is invalid")

    #   create the token access then yield it 
    access_token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/registration", response_model=user.UserPrivate)
async def register(
    user: user.UserCreate,
    db: AsyncSession = Depends(get_db), 
):
    hashed_pass = hash_password(user.password)

    result = await db.execute(select(User).where(User.username == user.username))
    user_found = result.scalar_one_or_none()
    
    if user_found:
        raise HTTPException(status_code=401, detail="user already exists")

    result_found = await db.execute(select(User).where(User.email == user.email.lower()))
    email_found = result_found.scalar_one_or_none()
    if email_found:
        raise HTTPException(status_code=401, detail="email already exists")

    reg_user = User(
        username = user.username,
        email = user.email.lower(),
        password_hash = hashed_pass,
        role = user.role,
    )

    db.add(reg_user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=404, detail="integrity error")

    await db.refresh(reg_user)
    return reg_user

@router.get("/me", response_model=user.UserPrivate)
async def me(user: User = Depends(auth.get_current_user)):
    return user