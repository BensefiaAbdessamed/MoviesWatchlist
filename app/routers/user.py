from sqlite3 import IntegrityError

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload
from app.database.session import get_db
from app.models.database import Movie, Review, User, Watchlist, Role
from app.schemas import user, watchlist, review
from app.core.auth import RoleChecker, get_current_user_id

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=list[user.UserPublic])
async def get_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(allowed_roles=[Role.ADMIN])),
):
    result = await db.execute(select(User))
    users = result.scalars().all()
    if not users:
        raise HTTPException(status_code=404, detail="No users to be found")
    return users


@router.get("/search", response_model=list[user.UserPublic])
async def find_user(username: str, db: AsyncSession = Depends(get_db)):
    # users = db.query(User).filter(User.username.startswith(username)).all()
    result =  await db.execute(select(User).where(User.username.startswith(username)))
    users = result.scalars().all()
    if not users:
        raise HTTPException(status_code=404, detail="No users to be found")
    return users
    

@router.get("/{user_id}", response_model=list[user.UserPublic])
async def get_user(user_id : int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="No users to be found")
    return user

@router.delete("/")
async def remove_user(
    user_id : int,
    user: User = Depends(RoleChecker(allowed_roles=[Role.ADMIN])), 
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user_ = result.scalar_one_or_none()
    await db.delete(user_)
    await db.commit()

@router.get("/{user_id}/watchlist", response_model=list[watchlist.WatchlistRead])
async def get_watchlist(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    # watchlist = db.query(Watchlist).filter(Watchlist.user_id == user_id).all()
    result = await db.execute(
        select(Watchlist)
        .where(Watchlist.user_id == user_id),
    )
    watchlist = result.scalars().all()
    if not watchlist:
        raise HTTPException(status_code=404, detail="No watchlist")
    return watchlist
    
@router.post("/{user_id}/watchlist", response_model=watchlist.WatchlistRead)
async def add_to_watchlist(
    the_watchlist: watchlist.WatchlistCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):

    # the_movie = db.query(Movie).filter(Movie.id == the_watchlist.movie_id).first()
    result = await db.execute(select(Movie).where(Movie.id == the_watchlist.movie_id))
    the_movie = result.scalar_one_or_none()
    
    if not the_movie:
        raise HTTPException(status_code=404, detail= "Movie not found")

    new_review = Watchlist(movie_id = the_watchlist.movie_id, Status = the_watchlist.status, user_id=user_id)
    statement = await db.execute(select(Watchlist).where(
        Watchlist.movie_id == the_watchlist.movie_id,
        Watchlist.user_id == user_id
    ))
    already = statement.scalar_one_or_none()
    
    if already:
        raise HTTPException(status_code=409, detail="already exists this watchlist")
    db.add(new_review)
    
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="can't add watchlist")

    await db.refresh(new_review)
    return new_review

@router.post("/{user_id}/{movie_id}/review", response_model=review.ReviewRead)
async def add_review(
    movie_id: int,
    the_review : review.ReviewCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(Movie).where(Movie.id == movie_id))
    the_movie = result.scalar_one_or_none()
    
    if not the_movie:
        raise HTTPException(status_code=404, detail="user not found")

    new_review = Review(user_id = user_id, movie_id = movie_id, **the_review.model_dump())
    db.add(new_review)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="can't add watchlist")

    await db.refresh(new_review)
    return new_review

    
    
    

    

