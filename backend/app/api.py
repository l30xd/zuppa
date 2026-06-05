from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core import get_db, get_default_user
from app.models.user import (
    User,
    Ingredient,
    RecipeHistory,
    IngredientCreate,
    IngredientUpdate,
    IngredientOut,
    RecipeGenerateRequest,
    RecipeHistoryOut,
    FavoriteToggle,
)
from app.services.llm_service import generate_recipes

router = APIRouter()


# Ingredients
@router.get("/ingredients/", response_model=list[IngredientOut])
async def list_ingredients(
    current_user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Ingredient)
        .where(Ingredient.user_id == current_user.id)
        .order_by(Ingredient.name)
    )
    return result.scalars().all()


@router.post("/ingredients/", response_model=IngredientOut, status_code=status.HTTP_201_CREATED)
async def add_ingredient(
    data: IngredientCreate,
    current_user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(
        select(Ingredient).where(
            Ingredient.user_id == current_user.id,
            Ingredient.name == data.name.lower().strip(),
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"'{data.name}' ya está en tu inventario.")

    ingredient = Ingredient(
        user_id=current_user.id,
        name=data.name.lower().strip(),
        quantity=data.quantity,
        category=data.category,
    )
    db.add(ingredient)
    await db.flush()
    await db.refresh(ingredient)
    return ingredient


@router.post("/ingredients/bulk", response_model=list[IngredientOut], status_code=status.HTTP_201_CREATED)
async def add_bulk(
    items: list[IngredientCreate],
    current_user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db),
):
    existing_result = await db.execute(
        select(Ingredient.name).where(Ingredient.user_id == current_user.id)
    )
    existing_names = {r for r in existing_result.scalars()}

    new_items = []
    for item in items:
        name = item.name.lower().strip()
        if name not in existing_names:
            ing = Ingredient(user_id=current_user.id, name=name, quantity=item.quantity, category=item.category)
            db.add(ing)
            new_items.append(ing)
            existing_names.add(name)

    await db.flush()
    for ing in new_items:
        await db.refresh(ing)
    return new_items


@router.patch("/ingredients/{ingredient_id}", response_model=IngredientOut)
async def update_ingredient(
    ingredient_id: str,
    data: IngredientUpdate,
    current_user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Ingredient).where(
            Ingredient.id == ingredient_id,
            Ingredient.user_id == current_user.id,
        )
    )
    ing = result.scalar_one_or_none()
    if not ing:
        raise HTTPException(status_code=404, detail="Ingrediente no encontrado.")

    if data.quantity is not None:
        ing.quantity = data.quantity
    if data.category is not None:
        ing.category = data.category
    await db.flush()
    await db.refresh(ing)
    return ing


@router.delete("/ingredients/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ingredient(
    ingredient_id: str,
    current_user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Ingredient).where(
            Ingredient.id == ingredient_id,
            Ingredient.user_id == current_user.id,
        )
    )
    ing = result.scalar_one_or_none()
    if not ing:
        raise HTTPException(status_code=404, detail="Ingrediente no encontrado.")
    await db.delete(ing)


@router.delete("/ingredients/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_inventory(
    current_user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db),
):
    await db.execute(
        delete(Ingredient).where(Ingredient.user_id == current_user.id)
    )


# Recipes
@router.post("/recipes/generate", response_model=list[RecipeHistoryOut])
async def generate(
    request: RecipeGenerateRequest,
    current_user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db),
):
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


@router.get("/recipes/history", response_model=list[RecipeHistoryOut])
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


@router.patch("/recipes/history/{recipe_id}/favorite", response_model=RecipeHistoryOut)
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


@router.delete("/recipes/history/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
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


@router.delete("/recipes/history", status_code=status.HTTP_204_NO_CONTENT)
async def clear_history(
    current_user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db),
):
    await db.execute(
        delete(RecipeHistory).where(RecipeHistory.user_id == current_user.id)
    )
