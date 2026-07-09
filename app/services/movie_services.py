from sqlalchemy.ext.asyncio import AsyncSession
from sqlite3 import IntegrityError
from app.models.database import Movie, Review, User, Role
from sqlalchemy import select
from fastapi import HTTPException
from app.schemas import movie


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

async def get_movies(db: AsyncSession):
    result =  await db.execute(select(Movie))
    all_movies = result.scalars().all()
    if not all_movies:
        raise HTTPException(status_code=404, detail="No movies to be found")
    return all_movies

async def add_movie(
    new_movie: movie.MovieCreate,
    db: AsyncSession,
):
    movie = Movie(**new_movie.model_dump())
    db.add(movie)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Movie already exists")
      
    return movie  

async def remove_movie(
    movie_id: int,
    db: AsyncSession,
):
    result =  await db.execute(select(Movie).where(Movie.id == movie_id))
    movie = result.scalar_one_or_none
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    await db.delete(movie)
    await db.commit()

async def get_movie_reviews(
    movie_id: int,
    db: AsyncSession
):
    result =  await db.execute(select(Review).where(Review.movie_id == movie_id))
    reviews = result.scalars().all()
    if not reviews:
        raise HTTPException(status_code=404, detail="no reviews for this film")   
    return reviews 