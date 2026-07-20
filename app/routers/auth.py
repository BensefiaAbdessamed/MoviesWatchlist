from fastapi import APIRouter, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.database.session import get_db
from app.models.database import User
from app.schemas import user
from app.core import auth
from app.services import auth_services

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    return await auth_services.login(response, form_data, db)
    
@router.post("/registration")
async def register(
    response: Response,
    user: user.UserCreate,
    db: AsyncSession = Depends(get_db), 
):
    return await auth_services.register(response, user, db)

@router.get("/me", response_model=user.UserPrivate)
async def me(user: User = Depends(auth.get_current_user)):
    return user

@router.post("/refresh")
async def refresh(
  request: Request,
  response: Response,
  db: AsyncSession = Depends(get_db)
):
    return await auth_services.refresh(
        request,
        response,
        db
    )

@router.post("/logout")
async def logout(
    response: Response,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth.get_current_user)
):
    return await auth_services.logout(
        response,
        db,
        user,
    )