import logging
from typing import Dict
import re
import ast

logger = logging.getLogger(__name__)


def clean_recipe_ingredients(recipe: Dict) -> Dict:
    """
    Cleans the 'ingredients_cleaned' field by correctly parsing the stored
    string representation of a list.
    """
    title = recipe.get('title', 'Unknown Recipe')
    logger.info(f"--- Cleaning ingredients for: {title} ---")

    ingredients_data = recipe.get("ingredients_cleaned", [])

    if not ingredients_data:
        logger.info("No ingredients data found.")
        recipe["ingredients_cleaned"] = []
        return recipe

    # Join the list into a single string that looks like a Python list literal
    # e.g., "['item 1', 'item 2', '...']"
    full_string = "".join(ingredients_data)

    clean_list = []
    try:
        # Use ast.literal_eval to safely parse the string into a Python list
        parsed_list = ast.literal_eval(full_string)

        if isinstance(parsed_list, list):
            # Clean up each item in the parsed list
            for item in parsed_list:
                clean_item = str(item).strip()
                if clean_item:
                    clean_list.append(clean_item)
            logger.info(f"Successfully parsed and cleaned {len(clean_list)} ingredients.")
        else:
            logger.warning("Parsed data is not a list.")

    except (ValueError, SyntaxError) as e:
        logger.error(f"Failed to parse ingredients string: {e}")
        # Fallback for safety, though the primary method should work for the given format
        recipe["ingredients_cleaned"] = []
        return recipe

    recipe["ingredients_cleaned"] = clean_list

    return recipe