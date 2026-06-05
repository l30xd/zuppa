import json
import httpx
from typing import Any

from app.core.config import settings


SYSTEM_PROMPT = """Eres un chef profesional experto en cocina latinoamericana y mundial.
Tu tarea es generar recetas creativas, deliciosas y prácticas basadas en los ingredientes
que el usuario tiene disponibles. Siempre respondes ÚNICAMENTE con JSON válido, sin texto
adicional, sin backticks, sin explicaciones fuera del JSON."""


def _build_user_prompt(
    ingredients: list[str],
    preferences: dict,
) -> str:
    time_map = {"rapida": "≤20 minutos", "media": "20-45 minutos", "elaborada": "más de 45 minutos"}
    diff_map = {"facil": "fácil (apto para principiantes)", "media": "media", "avanzada": "avanzada (chef experimentado)"}

    return f"""El usuario tiene estos ingredientes en casa: {', '.join(ingredients)}.

Preferencias:
- Tiempo de preparación: {time_map.get(preferences.get('time', 'media'), 'media')}
- Dificultad: {diff_map.get(preferences.get('difficulty', 'media'), 'media')}
- Restricción dietética: {preferences.get('diet', 'ninguna')}
- Número de recetas a generar: {preferences.get('count', 2)}

Genera exactamente {preferences.get('count', 2)} receta(s). Para cada receta puedes usar
ingredientes básicos adicionales (sal, aceite, agua, especias comunes) que no estén en la lista.

Responde SOLO con este JSON (array):
[
  {{
    "nombre": "Nombre atractivo de la receta",
    "descripcion": "Una línea describiendo el plato",
    "tiempo": "X min",
    "dificultad": "Fácil|Media|Avanzada",
    "porciones": 2,
    "calorias": "XXX kcal",
    "ingredientes": [
      {{"nombre": "ingrediente", "cantidad": "X unidades", "esDelInventario": true}},
      {{"nombre": "sal", "cantidad": "al gusto", "esDelInventario": false}}
    ],
    "pasos": [
      "Paso 1 detallado.",
      "Paso 2 detallado."
    ],
    "consejos": "Tip opcional del chef."
  }}
]"""


async def generate_recipes(
    ingredients: list[str],
    preferences: dict,
) -> list[dict[str, Any]]:
    """Llama a OpenRouter y devuelve las recetas parseadas."""
    if not ingredients:
        raise ValueError("Se necesita al menos un ingrediente.")

    payload = {
        "model": settings.OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(ingredients, preferences)},
        ],
        "temperature": 0.8,
        "max_tokens": 3000,
    }

    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "HTTP-Referer": settings.FRONTEND_URL,
        "X-Title": settings.APP_NAME,
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{settings.OPENROUTER_BASE_URL}/chat/completions",
            json=payload,
            headers=headers,
        )
        response.raise_for_status()

    data = response.json()
    raw_text = data["choices"][0]["message"]["content"]

    # Limpiar posibles backticks
    clean = raw_text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    recipes = json.loads(clean)

    if not isinstance(recipes, list):
        raise ValueError("El LLM no devolvió un array de recetas.")

    return recipes
