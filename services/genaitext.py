import os
import json
import requests
from typing import List, Dict, Optional
from PIL import Image
from io import BytesIO
from core.config import settings
from services.ingredient_recognizer import recognize_ingredients_from_image

# --- Configure the Gemini API client ---
# try:
#     genai.configure(api_key=settings.GEMINI_API_KEY)
# except Exception as e:
#     print(f"Error configuring Gemini API: {e}")


def generate_recipe_with_openrouter(ingredients: List[str]) -> Dict:
    """
    Generates a recipe using the OpenRouter API based on a list of ingredients.
    """
    headers = {
        "Authorization": f"{settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    ingredient_text = ", ".join(ingredients)

    prompt = f"""
    You are a master chef. Create a recipe using the following ingredients: {ingredient_text}.
    Your response must be a single, valid JSON object.
    The JSON object must have the following keys: "title", "ingredients", and "instructions".
    - "title": A creative name for the recipe.
    - "ingredients": A list of strings, where each string is an ingredient.
    - "instructions": A single string with the steps to prepare the recipe, separated by newlines.

    Example response:
    {{
      "title": "Spicy Tomato and Onion Pasta",
      "ingredients": [
        "1 pound spaghetti",
        "2 tablespoons olive oil",
        "1 large onion, chopped",
        "3 cloves garlic, minced",
        "1 (28 ounce) can crushed tomatoes",
        "1 teaspoon red pepper flakes",
        "Salt and pepper to taste",
        "Fresh basil for garnish"
      ],
      "instructions": "1. Cook spaghetti according to package directions.\\n2. While pasta is cooking, heat olive oil in a large skillet over medium heat. Add onion and cook until softened, about 5 minutes.\\n3. Add garlic and red pepper flakes and cook for another minute until fragrant.\\n4. Stir in crushed tomatoes, salt, and pepper. Bring to a simmer and cook for 10-15 minutes, stirring occasionally.\\n5. Drain spaghetti and add to the skillet with the sauce. Toss to combine.\\n6. Serve immediately, garnished with fresh basil."
    }}
    """

    data = {
        "model": "liquid/lfm-2.5-1.2b-instruct:free",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps(data)
        )
        response.raise_for_status()
        response_json = response.json()

        if response_json.get("choices"):
            assistant_message = response_json["choices"][0]["message"]["content"]
            # The model might return a string that is a JSON object.
            # We need to parse it.
            try:
                return json.loads(assistant_message)
            except json.JSONDecodeError:
                return {"error": "Failed to parse model response as JSON.", "raw_response": assistant_message}
        else:
            return {"error": "No response from model", "details": response_json}

    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

# --- Example Usage ---
if __name__ == "__main__":
    IMAGE_PATH = "img.png"
    print(f"Starting recipe generation pipeline for image: {IMAGE_PATH}\n")

    # 1. Recognize ingredients from the image
    recognized_ingredients = recognize_ingredients_from_image(IMAGE_PATH)

    if recognized_ingredients:
        print("\n--- Recognized Ingredients ---")
        print(recognized_ingredients)

        # 2. Generate the recipe with the recognized ingredients
        print("\n--- Generating Recipe ---")
        generated_recipe = generate_recipe_with_openrouter(recognized_ingredients)

        if "error" not in generated_recipe:
            print("\n--- Generated Recipe ---")
            print(json.dumps(generated_recipe, indent=2))
        else:
            print("\nCould not generate recipe.")
            print(json.dumps(generated_recipe, indent=2))

    else:
        print("\nCould not recognize any ingredients from the image.")
