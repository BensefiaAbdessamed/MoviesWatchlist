from app.database import connection
from sqlalchemy import ForeignKey      
from sqlalchemy.orm import mapped_column, Mapped, relationship
import enum


class Role(enum.Enum):
    ADMIN = "admin"
    USER = "user"
    
class WatchStatus(enum.Enum):
    WATCHED = "watched"
    UNWATCHED = "unwatched"
    WATCHING = "watching"
    
class Movie(connection.base):
    __tablename__ = "movies"

    id : Mapped[int] = mapped_column(primary_key=True)
    title : Mapped[str] = mapped_column(unique=True, index=True)
    release_year : Mapped[int]
    length : Mapped[int]
    watchlist_entry : Mapped[list["Watchlist"]] = relationship(back_populates="movie", cascade="all, delete-orphan")
    review_entry : Mapped[list["Review"]] = relationship(back_populates="movie", cascade="all, delete-orphan")
    
class User(connection.base):
    __tablename__ = "users"

    id : Mapped[int] = mapped_column(primary_key=True)
    username : Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[Role] = mapped_column(default=Role.USER, nullable=False)
    watchlist_entry : Mapped[list["Watchlist"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    review_entry : Mapped[list["Review"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    
class Watchlist(connection.base):
    __tablename__ = "watchlist"
    
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    movie_id : Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True)
    Status : Mapped[WatchStatus]
    
    movie : Mapped["Movie"] = relationship(back_populates="watchlist_entry")
    user : Mapped["User"] = relationship(back_populates="watchlist_entry")
    
    
class Review(connection.base):
    __tablename__ = "reviews"
    
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key= True)
    movie_id : Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True)
    
    descreption: Mapped[str]
    rating: Mapped[int]
    
    movie : Mapped["Movie"] = relationship(back_populates="review_entry")
    user : Mapped["User"] = relationship(back_populates="review_entry")


connection.base.metadata.create_all(bind=connection.engine)  