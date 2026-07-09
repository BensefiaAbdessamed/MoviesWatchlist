from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlite3 import IntegrityError
from app.models.database import User
from sqlalchemy import select
from fastapi import HTTPException
from app.schemas import user
from app.core.auth import create_access_token, hash_password, verify_password

async def login(
    form_data: OAuth2PasswordRequestForm,
    db: AsyncSession
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

async def register(
    user: user.UserCreate,
    db: AsyncSession 
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