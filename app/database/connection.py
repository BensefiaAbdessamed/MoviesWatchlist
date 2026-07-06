from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.schema import MetaData

SQLALCHEMY_DATABASE_URL = "sqlite:///./watchlist.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  ,
    echo = False,
)

base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

base.metadata.create_all(bind=engine)   