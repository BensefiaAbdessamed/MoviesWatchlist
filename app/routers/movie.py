from sqlite3.dbapi2 import IntegrityError
from sqlalchemy import select
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import RoleChecker, Role
from app.database.session import get_db
from app.models.database import Movie, Review, User
from app.schemas import movie, review
from app.services import movie_services

router = APIRouter(prefix="/movies", tags=["movie"])

@router.get("/search", response_model=list[movie.MovieRead])
async def find_movie(title: str, db: AsyncSession = Depends(get_db)):
    return await movie_services.find_movie(title, db)
    
@router.get("/{movie_id}", response_model=movie.MovieRead)
async def get_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    return await movie_services.get_movie(movie_id, db)
    
@router.get("/", response_model=list[movie.MovieRead])
async def get_movies(db: AsyncSession = Depends(get_db)):
    return await movie_services.get_movies(db)


@router.post("/", response_model= movie.MovieRead)
async def add_movie(
    new_movie: movie.MovieCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(allowed_roles=[Role.ADMIN])),
):
    return await movie_services.add_movie(new_movie, db)

@router.delete("/")
async def remove_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(allowed_roles=[Role.ADMIN])),
):
    return await movie_services.remove_movie(movie_id, db)

@router.get("/{movie_id}/reviews", response_model=list[review.ReviewRead])
async def get_movie_reviews(movie_id: int,  db: AsyncSession = Depends(get_db)):

    return await movie_services.get_movie_reviews(movie_id, db)
    
    

    

 