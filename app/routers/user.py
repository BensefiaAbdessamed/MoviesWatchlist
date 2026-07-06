from sqlite3 import IntegrityError

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.connection import SessionLocal
from app.models.database import Movie, Review, User, Watchlist, Role
from app.schemas import user, watchlist, review
from app.core.auth import RoleChecker, hash_password, get_current_user, get_current_user_id

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=list[user.UserPublic])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(allowed_roles=[Role.ADMIN])),
):
    users = db.query(User).all()
    if not users:
        raise HTTPException(status_code=404, detail="No users to be found")
    return users


@router.get("/search", response_model=list[user.UserPublic])
def find_user(username: str, db: Session = Depends(get_db)):
    users = db.query(User).filter(User.username.startswith(username)).all()
    if not users:
        raise HTTPException(status_code=404, detail="No users to be found")
    return users
    

@router.get("/{user_id}", response_model=list[user.UserPublic])
def get_user(user_id : int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first
    if not user:
        raise HTTPException(status_code=404, detail="No users to be found")
    return user

@router.delete("/")
def remove_user(
    user_id : int,
    user: User = Depends(RoleChecker(allowed_roles=[Role.ADMIN])), 
    db: Session = Depends(get_db),
):
    user_ = db.query(User).filter(User.id == user_id).first()
    db.delete(user_)
    db.commit()

@router.get("/{user_id}/watchlist", response_model=list[watchlist.WatchlistRead])
def get_watchlist(
    user_id: int,
    db: Session = Depends(get_db),
):
    watchlist = db.query(Watchlist).filter(Watchlist.user_id == user_id).all()
    if not watchlist:
        raise HTTPException(status_code=404, detail="No watchlist")
    return watchlist
    
@router.post("/{user_id}/watchlist", response_model=watchlist.WatchlistRead)
def add_to_watchlist(
    the_watchlist: watchlist.WatchlistCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):

    the_movie = db.query(Movie).filter(Movie.id == the_watchlist.movie_id).first()
    if not the_movie:
        raise HTTPException(status_code=404, detail= "Movie not found")

    new_review = Watchlist(movie_id = the_watchlist.movie_id, Status = the_watchlist.status, user_id=user_id)

    already = db.query(Watchlist).filter(
        Watchlist.movie_id == the_watchlist.movie_id,
        Watchlist.user_id == user_id
    ).first()
    
    if already:
        raise HTTPException(status_code=409, detail="already exists this watchlist")
    db.add(new_review)
    
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="can't add watchlist")

    db.refresh(new_review)
    return new_review

@router.post("/{user_id}/{movie_id}/review", response_model=review.ReviewRead)
def add_review(
    movie_id: int,
    the_review : review.ReviewCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)):

    the_movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not the_movie:
        raise HTTPException(status_code=404, detail="user not found")

    new_review = Review(user_id = user_id, movie_id = movie_id, **the_review.model_dump())
    db.add(new_review)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="can't add watchlist")

    db.refresh(new_review)
    return new_review

    
    
    

    

