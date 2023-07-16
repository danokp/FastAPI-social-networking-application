from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.models import User


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    '''Make the link between your database configuration and the users logic'''

    yield SQLAlchemyUserDatabase(session, User)
