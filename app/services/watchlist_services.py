from sqlalchemy.ext.asyncio import AsyncSession
from sqlite3 import IntegrityError
from app.models.database import Movie, Review, User, Watchlist, Role
from sqlalchemy import select
from fastapi import HTTPException
from app.schemas import user, watchlist, review

async def get_user_watchlist(
    user_id: int,
    db: AsyncSession
):
    result = await db.execute(
        select(Watchlist)
        .where(Watchlist.user_id == user_id),
    )
    watchlist_ = result.scalars().all()
    if not watchlist_:
        raise HTTPException(status_code=404, detail="No watchlist")
    return watchlist_

async def add_to_watchlist(
    the_watchlist: watchlist.WatchlistCreate,
    user_id: int,
    db: AsyncSession
):
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

    