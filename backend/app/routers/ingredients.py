from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.database import get_db
from app.core.security import get_default_user
from app.models.user import User, Ingredient
from app.schemas.schemas import IngredientCreate, IngredientUpdate, IngredientOut

router = APIRouter()


@router.get("/", response_model=list[IngredientOut])
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


@router.post("/", response_model=IngredientOut, status_code=status.HTTP_201_CREATED)
async def add_ingredient(
    data: IngredientCreate,
    current_user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db),
):
    # Verificar duplicado
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


@router.post("/bulk", response_model=list[IngredientOut], status_code=status.HTTP_201_CREATED)
async def add_bulk(
    items: list[IngredientCreate],
    current_user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db),
):
    """Agregar múltiples ingredientes a la vez. Ignora duplicados."""
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


@router.patch("/{ingredient_id}", response_model=IngredientOut)
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


@router.delete("/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
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


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_inventory(
    current_user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db),
):
    """Vaciar todo el inventario."""
    await db.execute(
        delete(Ingredient).where(Ingredient.user_id == current_user.id)
    )
