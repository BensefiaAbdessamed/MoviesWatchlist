from pydantic import BaseModel, Field
from app.models.database import WatchStatus

class WatchlistBase(BaseModel):
    movie_id: int
    status: WatchStatus | None = Field(default=WatchStatus.UNWATCHED)

class WatchlistCreate(WatchlistBase):
    pass

class WatchlistUpdate(BaseModel):
    status: WatchStatus

class WatchlistRead(WatchlistBase):
    user_id: int

    class Config:
        from_attributes = True
    

