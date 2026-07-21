from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.database.session import get_db
from app.models.database import User
from app.schemas import review, user, watchlist
from app.services import review_services, watchlist_services

router = APIRouter(prefix="/me", tags=["me"])

@router.get("/", response_model=user.UserPrivate)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user

@router.get("/watchlist", response_model=list[watchlist.WatchlistRead])
async def get_my_watchlist(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await watchlist_services.get_user_watchlist(current_user.id, db)

@router.post("/watchlist", response_model=watchlist.WatchlistRead)
async def add_to_my_watchlist(
    the_watchlist: watchlist.WatchlistCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await watchlist_services.add_to_watchlist(the_watchlist, current_user.id, db)

@router.patch("/watchlist/{movie_id}", response_model=watchlist.WatchlistRead)
async def update_my_watchlist_status(
    movie_id: int,
    the_watchlist: watchlist.WatchlistUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await watchlist_services.update_watchlist_status(
        movie_id,
        the_watchlist,
        current_user.id,
        db,
    )

@router.delete("/watchlist/{movie_id}")
async def remove_from_my_watchlist(
    movie_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await watchlist_services.remove_from_watchlist(movie_id, current_user.id, db)

@router.get("/reviews", response_model=list[review.ReviewRead])
async def get_my_reviews(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await review_services.get_user_reviews(current_user.id, db)
