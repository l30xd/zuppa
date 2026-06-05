from pydantic_settings import BaseSettings, SettingsConfigDict

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from passlib.context import CryptContext
from fastapi import Depends
from sqlalchemy import select


class Settings(BaseSettings):
	model_config = SettingsConfigDict(env_file=".env", extra="ignore")

	APP_NAME: str = "Zuppa"
	ENVIRONMENT: str = "development"
	FRONTEND_URL: str = "http://localhost:5173"
	DEFAULT_USER: str = "zuppa"

	# Base de datos
	DATABASE_URL: str

	# LLM
	OPENROUTER_API_KEY: str
	OPENROUTER_MODEL: str = "openai/gpt-4o-mini"
	OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"


settings = Settings()


# --- Database ---
engine = create_async_engine(
	settings.DATABASE_URL,
	echo=(settings.ENVIRONMENT == "development"),
	pool_size=10,
	max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
	bind=engine,
	expire_on_commit=False,
	class_=AsyncSession,
)


class Base(DeclarativeBase):
	pass


async def get_db():
	async with AsyncSessionLocal() as session:
		try:
			yield session
			await session.commit()
		except Exception:
			await session.rollback()
			raise


# --- Security helpers ---
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
	return pwd_context.hash(password)


async def get_default_user(db: AsyncSession = Depends(get_db)):
	# import here to avoid circular imports at module import time
	from app.models.user import User

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

