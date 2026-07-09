from sqlalchemy.ext.asyncio import AsyncSession
from sqlite3 import IntegrityError
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
        raise HTTPException(status_code=404, detail="user not found")

    new_review = Review(user_id = user_id, movie_id = movie_id, **review.model_dump())
    db.add(new_review)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="can't add watchlist")

    await db.refresh(new_review)
    return new_review

async def get_reviews(
    db: AsyncSession
):
    result =  await db.execute(select(Review))
    reviews = result.scalars().all()
    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews")
    return reviews

async def get_film_reviews(movie_id: int, db: AsyncSession):
    result = await db.execute(select(Review).where(Review.movie_id == movie_id))
    the_review = result.scalars().all()

    if not the_review:
        raise HTTPException(status_code=404, detail="review not found")   
    return the_review

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
        raise HTTPException(status_code=404, detail="review not found")
    await db.delete(review)
    await db.commit()