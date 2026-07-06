from pydantic import BaseModel, ConfigDict, Field, EmailStr
from app.models.database import WatchStatus

class ReviewBase(BaseModel):
    descreption: str | None = None
    rating: int | None =  Field(default= None, ge = 0, le = 5)

class ReviewCreate(ReviewBase):
    pass

class ReviewRead(ReviewBase):
    user_id: int
    movie_id: int
    
    class Config:
        from_attributes = True
    

