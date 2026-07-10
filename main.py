from fastapi import FastAPI
from app.database.connection import SessionLocal, lifespan
from app.exceptions import (
    user_exceptions, 
    movie_exceptions, 
    review_exceptions, 
    wathclist_exceptions, 
    auth_exceptions
) 
from app.routers import review, user, movie, auth

app = FastAPI(lifespan=lifespan)

app.include_router(movie.router)
app.include_router(user.router)
app.include_router(review.router)
app.include_router(auth.router)

app.add_exception_handler(
    user_exceptions.UserNotFoundError,
    user_exceptions.user_not_found_handler,
)

app.add_exception_handler(
    user_exceptions.AlreadyExists,
    user_exceptions.already_exists_handler,
)

app.add_exception_handler(
    movie_exceptions.MovieNotFoundError,
    movie_exceptions.movie_not_found_handler,
)
app.add_exception_handler(
    movie_exceptions.MovieAlreadyExists,
    movie_exceptions.movie_already_exists_handler,
)


app.add_exception_handler(
    review_exceptions.ReviewNotFoundError,
    review_exceptions.review_not_found_handler,
)
app.add_exception_handler(
    review_exceptions.ReviewAlreadyExists,
    review_exceptions.review_already_exists_handler,
)

app.add_exception_handler(
    wathclist_exceptions.WatchlistNotFoundError,
    wathclist_exceptions.watchlist_not_found_handler,
)

app.add_exception_handler(
    wathclist_exceptions.WatchlistAlreadyExists,
    wathclist_exceptions.watchlist_already_exists_handler,
)
app.add_exception_handler(
    auth_exceptions.NotAuthenticatedError,
    auth_exceptions.not_authenticated_handler,
)





