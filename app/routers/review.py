from sqlite3.dbapi2 import IntegrityError
from sqlalchemy import select
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.models.database import Review, User
from app.schemas import review
from app.core.auth import get_current_user, RoleChecker, Role
from app.services import review_services


router = APIRouter(prefix ="/reviews", tags=["reviews"])
@router.get("/", response_model=list[review.ReviewRead])
async def get_reviews(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(allowed_roles=[Role.ADMIN])),
):
    return await review_services.get_reviews(db)


@router.delete("/")
async def remove_review(
    movie_id: int,
    user: User = Depends(get_current_user),              
    db: AsyncSession = Depends(get_db),
):
    return await review_services.remove_review(movie_id, user, db)

@router.get("/{movie_id}/reviews", response_model=list[review.ReviewRead])
async def get_movie_reviews(movie_id: int,  db: AsyncSession = Depends(get_db)):

    return await review_services.get_movie_reviews(movie_id, db)