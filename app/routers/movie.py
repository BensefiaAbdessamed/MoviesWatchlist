from sqlite3.dbapi2 import IntegrityError
from sqlalchemy import select
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import RoleChecker, Role
from app.database.session import get_db
from app.models.database import Movie, Review, User
from app.schemas import movie, review

router = APIRouter(prefix="/movies", tags=["movie"])

@router.get("/search", response_model=list[movie.MovieRead])
async def find_movie(title: str, db: AsyncSession = Depends(get_db)):
    # movies = db.query(Movie).filter(Movie.title.startswith(title)).all()
    result =  await db.execute(select(Movie).where(Movie.title.startswith(title)))
    movies = result.scalars().all()
    if not movies:
        raise HTTPException(status_code=404, detail="No movies to be found")
    return movies
    
@router.get("/{movie_id}", response_model=movie.MovieRead)
async def get_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    # the_movie = db.query(Movie).filter(Movie.id == movie_id).first()
    result =  await db.execute(select(Movie).where(Movie.id == movie_id))
    the_movie = result.scalar_one_or_none
    if not the_movie:
        raise HTTPException(status_code=404, detail="Movie not found")   
    return the_movie

@router.get("/", response_model=list[movie.MovieRead])
async def get_movies(db: AsyncSession = Depends(get_db)):
    # all_movies = db.query(Movie).all()
    result =  await db.execute(select(Movie))
    all_movies = result.scalars().all()
    if not all_movies:
        raise HTTPException(status_code=404, detail="No movies to be found")
    return all_movies


@router.post("/", response_model= movie.MovieRead)
async def add_movie(
    new_movie: movie.MovieCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(allowed_roles=[Role.ADMIN])),
):
    movie = Movie(**new_movie.model_dump())
    db.add(movie)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Movie already exists")
      
    return movie  

@router.delete("/")
async def remove_movie(
    movie_id = Movie.id,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(allowed_roles=[Role.ADMIN])),
):
    # movie = db.query(Movie).filter(Movie.id == movie_id).first()
    result =  await db.execute(select(Movie).where(Movie.id == movie_id))
    movie = result.scalar_one_or_none
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    await db.delete(movie)
    await db.commit()

@router.get("/{movie_id}/reviews", response_model=list[review.ReviewRead])
async def get_movie_reviews(movie_id: int,  db: AsyncSession = Depends(get_db)):
    # reviews = db.query(Review).filter(Review.movie_id == movie_id).all()
    result =  await db.execute(select(Review).where(Review.movie_id == movie_id))
    reviews = result.scalars().all()
    if not reviews:
        raise HTTPException(status_code=404, detail="no reviews for this film")   
    return reviews    
    
    

    

 