# stir-backend/crud/crud_recipe.py

from db.mongodb import db
from typing import List
from bson import ObjectId

COLLECTION_NAME = "recipes"


async def get_recipes(skip: int = 0, limit: int = 100) -> List[dict]:
    """
    Retrieves a list of recipes with pagination.
    """
    cursor = db[COLLECTION_NAME].find({}, skip=skip, limit=limit)
    return await cursor.to_list(length=limit)


async def get_recipe_by_id(recipe_id: str) -> dict:
    """
    Finds a single recipe by its unique ID.
    """
    try:
        # Convert string ID to BSON ObjectId
        obj_id = ObjectId(recipe_id)
    except Exception:
        # If the ID is not valid, it cannot be in the database.
        return None

    return await db[COLLECTION_NAME].find_one({"_id": obj_id})


async def find_recipes_by_ingredients(ingredients: List[str], limit: int = 50) -> List[dict]:
    """
    Finds recipes that contain ALL of the specified ingredients.

    Args:
        ingredients: A list of ingredient strings to search for.
        limit: The maximum number of recipes to return.

    Returns:
        A list of matching recipe documents from the database.
    """
    if not ingredients:
        return []

    # The $all operator matches arrays that contain all elements specified in the query.
    # We use a case-insensitive regex for each ingredient for better matching.
    query = {
        "ingredients_cleaned": {
            "$all": [f"(?i){ingredient.strip()}" for ingredient in ingredients]
        }
    }

    cursor = db[COLLECTION_NAME].find(query).limit(limit)
    return await cursor.to_list(length=limit)