from sqlite3.dbapi2 import IntegrityError
from sqlalchemy import select
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.models.database import Review, User
from app.schemas import review
from app.core.auth import get_current_user, RoleChecker, Role


router = APIRouter(prefix ="/reviews", tags=["reviews"])
@router.get("/", response_model=list[review.ReviewRead])
async def get_reviews(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(allowed_roles=[Role.ADMIN])),
):
    result =  await db.execute(select(Review))
    reviews = result.scalars().all()
    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews")
    return reviews
    
@router.get("/{movie_id}", response_model=list[review.ReviewRead])
async def get_film_reviews(movie_id: int, db: AsyncSession = Depends(get_db)):
    # the_review = db.query(Review).filter(Review.movie_id == movie_id).all()
    result = await db.execute(select(Review).where(Review.movie_id == movie_id))
    the_review = result.scalars().all()

    if not the_review:
        raise HTTPException(status_code=404, detail="review not found")   
    return the_review

@router.delete("/")
async def remove_review(
    movie_id: int,
    user: User = Depends(get_current_user),              
    db: AsyncSession = Depends(get_db),
):
    if user.role == Role.ADMIN:
        review = Review(
            Review.movie_id == movie_id,
        ).first()

    else:
        result = await db.execute(select(Review).where(
            Review.movie_id == movie_id,
            Review.user_id == user.id,
        ))
        review = result.scalar_one_or_none() 
    if not review:
        raise HTTPException(status_code=404, detail="review not found")
    await db.delete(review)
    await db.commit()
