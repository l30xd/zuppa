import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from sqlalchemy import String, Boolean, DateTime, ForeignKey, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pydantic import BaseModel, Field, ConfigDict

from app.core import Base


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    ingredients: Mapped[list["Ingredient"]] = relationship(back_populates="user", cascade="all, delete")
    recipe_history: Mapped[list["RecipeHistory"]] = relationship(back_populates="user", cascade="all, delete")


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    quantity: Mapped[str | None] = mapped_column(String(100))
    category: Mapped[str | None] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="ingredients")


class RecipeHistory(Base):
    __tablename__ = "recipe_history"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    ingredients_used: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    preferences: Mapped[dict | None] = mapped_column(JSONB)
    result: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="recipe_history")


# -----------------
# Pydantic schemas
# -----------------


class IngredientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    quantity: Optional[str] = Field(default=None, max_length=100)
    category: Optional[str] = Field(default=None, max_length=80)


class IngredientUpdate(BaseModel):
    quantity: Optional[str] = None
    category: Optional[str] = None


class IngredientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    quantity: Optional[str]
    category: Optional[str]
    created_at: datetime


class RecipePreferences(BaseModel):
    time: str = Field(default="media", pattern="^(rapida|media|elaborada)$")
    difficulty: str = Field(default="media", pattern="^(facil|media|avanzada)$")
    diet: str = Field(default="ninguna")
    count: int = Field(default=2, ge=1, le=5)


class RecipeGenerateRequest(BaseModel):
    preferences: RecipePreferences = RecipePreferences()


class RecipeHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    ingredients_used: Optional[list[str]]
    preferences: Optional[dict[str, Any]]
    result: dict[str, Any]
    is_favorite: bool
    created_at: datetime


class FavoriteToggle(BaseModel):
    is_favorite: bool
