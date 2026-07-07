from fastapi import FastAPI
from app.database.connection import SessionLocal, lifespan
from app.models import database
from app.routers import review, user, movie, watchlist, auth

app = FastAPI(lifespan=lifespan)

app.include_router(movie.router)
app.include_router(user.router)
app.include_router(review.router)
app.include_router(auth.router)

