from fastapi import APIRouter
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
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    return await auth_services.login(form_data, db)
    
@router.post("/registration", response_model=user.UserPrivate)
async def register(
    user: user.UserCreate,
    db: AsyncSession = Depends(get_db), 
):
    return await auth_services.register(user, db)

@router.get("/me", response_model=user.UserPrivate)
async def me(user: User = Depends(auth.get_current_user)):
    return user