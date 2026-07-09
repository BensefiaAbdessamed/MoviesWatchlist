from sqlalchemy.ext.asyncio import AsyncSession
from sqlite3 import IntegrityError
from app.models.database import Movie, Review, User, Role
from sqlalchemy import select
from fastapi import HTTPException
from app.schemas import review, movie, user


async def find_movie(
    title: str,
    db: AsyncSession
):
    result =  await db.execute(select(Movie).where(Movie.title.startswith(title)))
    movies = result.scalars().all()
    if not movies:
        raise HTTPException(status_code=404, detail="No movies to be found")
    return movies

async def get_movie(
    movie_id: int,
    db: AsyncSession
):
    result =  await db.execute(select(Movie).where(Movie.id == movie_id))
    the_movie = result.scalar_one_or_none
    if not the_movie:
        raise HTTPException(status_code=404, detail="Movie not found")   
    return the_movie