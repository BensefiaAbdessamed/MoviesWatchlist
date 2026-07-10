from sqlite3 import IntegrityError

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.database.session import get_db
from app.models.database import Movie, Review, User, Watchlist, Role
from app.schemas import user, watchlist, review
from app.core.auth import RoleChecker, get_current_user_id
from app.services import review_services, user_services, watchlist_services

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=list[user.UserPublic])
async def get_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(allowed_roles=[Role.ADMIN])),
):
    return await user_services.get_users(db=db)

@router.get("/search", response_model=list[user.UserPublic])
async def find_user(username: str, db: AsyncSession = Depends(get_db)):
    return await user_services.find_user(username, db)
    

@router.get("/{user_id}", response_model=list[user.UserPublic])
async def get_user(user_id : int, db: AsyncSession = Depends(get_db)):
    return await user_services.get_user(user_id=user_id, db=db)

@router.delete("/")
async def remove_user(
    user_id : int,
    user: User = Depends(RoleChecker(allowed_roles=[Role.ADMIN])), 
    db: AsyncSession = Depends(get_db),
):
    return await user_services.remove_user(user_id, db)

@router.get("/{user_id}/watchlist", response_model=list[watchlist.WatchlistRead])
async def get_user_watchlist(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(allowed_roles=[Role.ADMIN, Role.USER])),
):
    return await watchlist_services.get_user_watchlist(user_id, db)
    
@router.post("/{user_id}/watchlist", response_model=watchlist.WatchlistRead)
async def add_to_watchlist(
    the_watchlist: watchlist.WatchlistCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await watchlist_services.add_to_watchlist(the_watchlist, user_id, db)

@router.post("/{user_id}/{movie_id}/review", response_model=review.ReviewRead)
async def add_review(
    movie_id: int,
    the_review : review.ReviewCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await review_services.add_review(movie_id, the_review, user_id, db)

    
    
    

    

