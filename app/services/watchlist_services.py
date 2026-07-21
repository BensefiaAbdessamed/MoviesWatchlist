from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.exceptions.movie_exceptions import MovieNotFoundError
from app.exceptions.wathclist_exceptions import WatchlistAlreadyExists, WatchlistNotFoundError
from app.models.database import Movie, Watchlist
from sqlalchemy import select
from app.schemas import watchlist

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
        raise WatchlistNotFoundError(user_id)
    return watchlist_

async def add_to_watchlist(
    the_watchlist: watchlist.WatchlistCreate,
    user_id: int,
    db: AsyncSession
):
    #   CHECK IF THE MOVIE EXISTS BEFORE
    result = await db.execute(select(Movie).where(Movie.id == the_watchlist.movie_id))
    the_movie = result.scalar_one_or_none()
    
    if not the_movie:
        raise MovieNotFoundError(movie_id=the_watchlist.movie_id)

    new_watchlist = Watchlist(
        movie_id = the_watchlist.movie_id,
        Status = the_watchlist.status, 
        user_id=user_id
    )
    
    db.add(new_watchlist)
    
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise WatchlistAlreadyExists(the_watchlist.movie_id)

    await db.refresh(new_watchlist)
    return new_watchlist


async def update_watchlist_status(
    movie_id: int,
    the_watchlist: watchlist.WatchlistUpdate,
    user_id: int,
    db: AsyncSession
):
    result = await db.execute(
        select(Watchlist).where(
            Watchlist.movie_id == movie_id,
            Watchlist.user_id == user_id,
        )
    )
    watchlist_item = result.scalar_one_or_none()

    if not watchlist_item:
        raise WatchlistNotFoundError(user_id)

    watchlist_item.Status = the_watchlist.status
    await db.commit()
    await db.refresh(watchlist_item)
    return watchlist_item

async def remove_from_watchlist(
    movie_id: int,
    user_id: int,
    db: AsyncSession
):
    result = await db.execute(
        select(Watchlist).where(
            Watchlist.movie_id == movie_id,
            Watchlist.user_id == user_id,
        )
    )
    watchlist_item = result.scalar_one_or_none()

    if not watchlist_item:
        raise WatchlistNotFoundError(user_id)

    await db.delete(watchlist_item)
    await db.commit()
    return {
        "status code": 200,
        "detail": "movie removed from watchlist successfully"
    }

