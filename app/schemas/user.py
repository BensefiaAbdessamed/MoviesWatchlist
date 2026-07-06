from pydantic import BaseModel, ConfigDict, Field, EmailStr
from app.models.database import Role, WatchStatus

class UserBase(BaseModel):
    username: str
    email: EmailStr = Field(max_length=100)

class UserCreate(UserBase):
    password: str = Field(min_length=8)
    role: Role = Field(default=Role.USER)
    
class UserPublic(BaseModel):
    id: int
    username: str
    
class UserPrivate(UserPublic):
    email: EmailStr = Field(max_length=100)
    role: Role

    class Config:
        from_attributes = True

class Token(BaseModel):
    acess_token: str
    token_type: str

