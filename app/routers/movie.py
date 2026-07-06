from sqlite3.dbapi2 import IntegrityError

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.auth import RoleChecker, Role
from app.database.session import get_db
from app.database.connection import SessionLocal
from app.models.database import Movie, Review, User
from app.schemas import movie, review

router = APIRouter(prefix="/movies", tags=["movie"])

@router.get("/search", response_model=list[movie.MovieRead])
def find_movie(title: str, db: Session = Depends(get_db)):
    movies = db.query(Movie).filter(Movie.title.startswith(title)).all()
    if not movies:
        raise HTTPException(status_code=404, detail="No movies to be found")
    return movies
    
@router.get("/{movie_id}", response_model=movie.MovieRead)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    the_movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not the_movie:
        raise HTTPException(status_code=404, detail="Movie not found")   
    return the_movie

@router.get("/", response_model=list[movie.MovieRead])
def get_movies(db: Session = Depends(get_db)):
    all_movies = db.query(Movie).all()
    if not all_movies:
        raise HTTPException(status_code=404, detail="No movies to be found")
    return all_movies


@router.post("/", response_model= movie.MovieRead)
def add_movie(
    new_movie: movie.MovieCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(allowed_roles=[Role.ADMIN])),
):
    movie = Movie(**new_movie.model_dump())
    db.add(movie)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Movie already exists")
      
    return movie  

@router.delete("/")
def remove_movie(
    movie_id = Movie.id,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(allowed_roles=[Role.ADMIN])),
):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    db.delete(movie)
    db.commit()

@router.get("/{movie_id}/reviews", response_model=list[review.ReviewRead])
def get_movie_reviews(movie_id: int,  db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(Review.movie_id == movie_id).all()
    if not reviews:
        raise HTTPException(status_code=404, detail="no reviews for this film")   
    return reviews    
    
    

    

 