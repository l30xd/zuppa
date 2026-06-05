from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_default_user
from app.models.user import User, Ingredient, RecipeHistory
from app.schemas.schemas import RecipeGenerateRequest, RecipeHistoryOut, FavoriteToggle
from app.services.llm_service import generate_recipes

router = APIRouter()


@router.post("/generate", response_model=list[RecipeHistoryOut])
async def generate(
    request: RecipeGenerateRequest,
    current_user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db),
):
    # Obtener ingredientes del inventario del usuario
    result = await db.execute(
        select(Ingredient.name).where(Ingredient.user_id == current_user.id)
    )
    ingredient_names = [r for r in result.scalars()]

    if not ingredient_names:
        raise HTTPException(
            status_code=400,
            detail="Tu inventario está vacío. Agrega ingredientes primero.",
        )

    prefs_dict = request.preferences.model_dump()

    try:
        recipes_data = await generate_recipes(ingredient_names, prefs_dict)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Error al comunicarse con el LLM: {str(e)}",
        )

    # Guardar en historial
    history_records = []
    for recipe in recipes_data:
        used = [
            ing["nombre"]
            for ing in recipe.get("ingredientes", [])
            if ing.get("esDelInventario")
        ]
        record = RecipeHistory(
            user_id=current_user.id,
            title=recipe.get("nombre", "Receta sin nombre"),
            ingredients_used=used,
            preferences=prefs_dict,
            result=recipe,
        )
        db.add(record)
        history_records.append(record)

    await db.flush()
    for r in history_records:
        await db.refresh(r)

    return history_records


@router.get("/history", response_model=list[RecipeHistoryOut])
async def get_history(
    favorites_only: bool = False,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(RecipeHistory)
        .where(RecipeHistory.user_id == current_user.id)
        .order_by(RecipeHistory.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    if favorites_only:
        query = query.where(RecipeHistory.is_favorite.is_(True))

    result = await db.execute(query)
    return result.scalars().all()


@router.patch("/history/{recipe_id}/favorite", response_model=RecipeHistoryOut)
async def toggle_favorite(
    recipe_id: str,
    body: FavoriteToggle,
    current_user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RecipeHistory).where(
            RecipeHistory.id == recipe_id,
            RecipeHistory.user_id == current_user.id,
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Receta no encontrada.")

    record.is_favorite = body.is_favorite
    await db.flush()
    await db.refresh(record)
    return record


@router.delete("/history/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_history_entry(
    recipe_id: str,
    current_user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RecipeHistory).where(
            RecipeHistory.id == recipe_id,
            RecipeHistory.user_id == current_user.id,
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Receta no encontrada.")
    await db.delete(record)
