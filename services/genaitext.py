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
    Your response must be a single, valid JSON object that conforms to the following structure:
    {{
      "title": "A creative and fitting title for the recipe",
      "description": "A brief, appealing one-sentence description of the dish.",
      "servings": "e.g., 2-4 people",
      "prep_time": "e.g., 15 minutes",
      "cook_time": "e.g., 30 minutes",
      "ingredients": [
        {{ "item": "Full ingredient name", "quantity": "e.g., 2 cups or 100g" }}
      ],
      "instructions": [
        "Step-by-step instruction 1.",
        "Step-by-step instruction 2."
      ]
    }}

    Do not include any text, explanation, or markdown formatting before or after the JSON object.
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
