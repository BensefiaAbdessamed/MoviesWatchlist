from fastapi.responses import JSONResponse
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.core.config import settings
from app.exceptions.auth_exceptions import NotAuthenticatedError
from app.exceptions.user_exceptions import AlreadyExists
from app.models import database
from app.models.database import User
from sqlalchemy import select
from fastapi import HTTPException, Request, Response
from app.schemas import user
from app.core.auth import create_access_token, create_refresh_token, hash_password, verify_password, verify_refresh_token

async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm,
    db: AsyncSession
):
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()

    #   validate user cridentials
    if not user:
        raise NotAuthenticatedError()

    valid = verify_password(form_data.password, user.password_hash)
    if not valid:
        raise NotAuthenticatedError()

    #   create the access token and the refresh one 
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    user.refresh_token = refresh_token
    await db.commit()
    await db.refresh(user)
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60*60*24*14,
        path="/auth/refresh"
    )

    return {"access_token": access_token, "token_type": "bearer"}

async def register(
    response: Response,
    user: user.UserCreate,
    db: AsyncSession 
):
    hashed_pass = hash_password(user.password)

    result = await db.execute(select(User).where(User.username == user.username))
    user_found = result.scalar_one_or_none()
    
    if user_found:
        raise AlreadyExists("USER")
    result_found = await db.execute(select(User).where(User.email == user.email.lower()))
    email_found = result_found.scalar_one_or_none()

    if email_found:
        raise AlreadyExists("EMAIL")

    user = User(
        username = user.username,
        email = user.email.lower(),
        password_hash = hashed_pass,
        role = database.Role.USER
    )

    db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise AlreadyExists("USER CRIDENTIALS")
    await db.refresh(user)

    new_refresh_token = create_refresh_token({"sub": str(user.id)})
    user.refresh_token = new_refresh_token
    await db.commit()
    await db.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id)})
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60*60*24*14,
        path="/auth/refresh"
    )

    return {"access_token": access_token, "token_type": "bearer"}

async def refresh(
  request: Request,
  response: Response,
  db: AsyncSession
):
    #   extract the token from cookie
    token = request.cookies.get("refresh_token")

    if not token:
        raise HTTPException(status_code=401, detail="cannot find cookie")

    #   extract user credentials from the token
    try:
        decoded_token = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm]
        )
    except jwt.InvalidTokenError:
        raise NotAuthenticatedError()
    else:
        user_id = decoded_token.get("sub")

    #   validate credentials
    if not user_id:
        raise NotAuthenticatedError()

    result = await db.execute(select(User).filter(User.id == int(user_id)))
    user = result.scalar_one()

    if user.refresh_token != token:
        raise NotAuthenticatedError()
    
    #   create new access/refresh token
    access_token = create_access_token(data={"sub": str(user_id)})
    refresh_token = create_refresh_token(data={"sub": str(user_id)})

    user.refresh_token = refresh_token
    await db.commit()
    await db.refresh(user)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60*60*24*14,
        path="/auth/refresh"
    )

    #   return new acess token
    return {"access_token": access_token, "token_type": "bearer"}

async def logout(
  response: Response,
  db: AsyncSession,
  user: User
):
    response.delete_cookie(
        key="refresh_token",
        path="/auth/refresh",
    )

    result = await db.execute(select(User).filter(User.id == user.id))
    found_user = result.scalar_one()
    found_user.refresh_token = None

    return {
        "staus code" : 200,
        "detail" : "logged out successfully"
    }
    
            

    
    