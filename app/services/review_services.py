from sqlalchemy.ext.asyncio import AsyncSession
from sqlite3 import IntegrityError
from app.exceptions.movie_exceptions import MovieNotFoundError
from app.exceptions.review_exceptions import ReviewAlreadyExists, ReviewNotFoundError
from app.models.database import Movie, Review, User, Role
from sqlalchemy import select
from fastapi import HTTPException
from app.schemas import review



async def add_review(
    movie_id: int,
    review : review.ReviewCreate,
    user_id: int,
    db: AsyncSession
):

    result = await db.execute(select(Movie).where(Movie.id == movie_id))
    the_movie = result.scalar_one_or_none()
    
    if not the_movie:
        raise MovieNotFoundError(movie_id)

    # NO NEED TO CHECK FOR THE USER SINCE BEFORE CALLING THIS FUNCTION
    # ONLY A REAL USER CAN ADD REVIEW "AUTHENTICATED ROUTE"
    #
    new_review = Review(user_id = user_id, movie_id = movie_id, **review.model_dump())
    db.add(new_review)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ReviewAlreadyExists(movie_id)
        
    await db.refresh(new_review)
    return new_review

async def get_reviews(
    db: AsyncSession
):
    """used by admin only, just in case we wanna get all reviews..."""
    result =  await db.execute(select(Review))
    reviews = result.scalars().all()
    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews")
    return reviews


async def remove_review(
    movie_id: int,
    user_: User,
    db: AsyncSession
):
    if user_.role == Role.ADMIN:
        review = Review(
            Review.movie_id == movie_id,
        ).first()

    else:
        result = await db.execute(select(Review).where(
            Review.movie_id == movie_id,
            Review.user_id == user_.id,
        ))
        review = result.scalar_one_or_none() 
    if not review:
        raise ReviewNotFoundError(movie_id)
    await db.delete(review)
    await db.commit()

async def get_movie_reviews(
    movie_id: int,
    db: AsyncSession
):
    result =  await db.execute(select(Review).where(Review.movie_id == movie_id))
    reviews = result.scalars().all()
    if not reviews:
        raise ReviewNotFoundError(movie_id)  
    return reviews 