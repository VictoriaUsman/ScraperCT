from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_session


async def get_db(session: AsyncSession = Depends(get_session)) -> AsyncSession:
    return session
