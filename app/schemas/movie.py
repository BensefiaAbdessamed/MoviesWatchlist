from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.sql.operators import ge, le
from app.models.database import WatchStatus

class MovieBase(BaseModel):
    title : str
    release_year: int = Field(ge=1800, le=2026)
    length: int = Field(ge=1)

class MovieCreate(MovieBase):
    pass

class MovieRead(MovieBase):
    id: int

    class Config:
        from_attributes = True

