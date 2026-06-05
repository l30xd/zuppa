from passlib.context import CryptContext
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


async def get_default_user(
    db: AsyncSession = Depends(get_db),
) -> User:
    result = await db.execute(select(User).where(User.username == settings.DEFAULT_USER))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(
            email=f"{settings.DEFAULT_USER}@local",
            username=settings.DEFAULT_USER,
            hashed_password=hash_password(settings.DEFAULT_USER),
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
    return user
