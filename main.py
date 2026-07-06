from fastapi import FastAPI
from app.database.connection import SessionLocal, engine, base
from app.models import database
from app.routers import review, user, movie, watchlist, auth

app = FastAPI()

app.include_router(movie.router)
app.include_router(user.router)
app.include_router(review.router)
app.include_router(auth.router)

