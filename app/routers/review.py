from sqlite3.dbapi2 import IntegrityError

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.connection import SessionLocal
from app.models.database import Review, User
from app.schemas import review
from app.core.auth import get_current_user, RoleChecker, Role


router = APIRouter(prefix ="/reviews", tags=["reviews"])
@router.get("/", response_model=list[review.ReviewRead])
def get_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(allowed_roles=[Role.ADMIN])),
):
    reviews = db.query(Review).all()
    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews")
    return reviews
    
@router.get("/{movie_id}", response_model=list[review.ReviewRead])
def get_film_reviews(movie_id: int, db: Session = Depends(get_db)):
    the_review = db.query(Review).filter(Review.movie_id == movie_id).all()
    if not the_review:
        raise HTTPException(status_code=404, detail="review not found")   
    return the_review

@router.delete("/")
def remove_review(
    movie_id: int,
    user: User = Depends(get_current_user),              
    db: Session = Depends(get_db),
):
    if user.role == Role.ADMIN:
        review = Review(
            Review.movie_id == movie_id,
        ). first()

    else:
        review = db.query(Review).filter(
            Review.movie_id == movie_id,
            Review.user_id == user.id,
        ).first()

    if not review:
        raise HTTPException(status_code=404, detail="review not found")
    db.delete(review)
    db.commit()
