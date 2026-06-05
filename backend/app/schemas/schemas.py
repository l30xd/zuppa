from __future__ import annotations
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field, ConfigDict


# ── Ingredientes ──────────────────────────────────────────────────

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


# ── Recetas ───────────────────────────────────────────────────────

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
