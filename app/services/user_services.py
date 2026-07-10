from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.user_exceptions import UserNotFoundError
from app.models.database import User
from sqlalchemy import select
from fastapi import HTTPException

async def get_users(db: AsyncSession):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users

async def get_user(
    user_id: int,
    db: AsyncSession,
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise UserNotFoundError(user_id)
    return user

async def find_user(
    username:str,
    db: AsyncSession
):
    result =  await db.execute(select(User).where(User.username.startswith(username)))
    users = result.scalars().all()
    if not users:
        raise HTTPException(status_code=404, detail="No users to be found")
    return users

async def remove_user(
    user_id: int,
    db: AsyncSession
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    await db.delete(user)
    await db.commit()
    
    
    
    