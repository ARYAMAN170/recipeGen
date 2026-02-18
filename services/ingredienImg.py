import requests
import json
import base64
import os
from typing import List
from core.config import settings

def encode_image_to_base64(image_path: str) -> str:
    """Encodes an image file to a base64 string."""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found at: {image_path}")
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_ingredients_from_image(image_path: str) -> List[str]:
    """
    Extracts a list of ingredients from an image using the OpenRouter API.
    """
    try:
        base64_image = encode_image_to_base64(image_path)
    except FileNotFoundError as e:
        print(e)
        return []

    headers = {
        "Authorization": f"{settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "nvidia/nemotron-nano-12b-v2-vl:free",  # Vision model
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """
    Your task is to identify all edible food items in the image.
    - Focus only on the food ingredients.
    - Ignore non-food items (e.g., bowls, packaging, text).
    - Your entire response must be a single, valid JSON object.
    - The JSON object must have one key: "ingredients".
    - The value of "ingredients" must be an array of strings.
    - Do not include markdown, explanations, or any text outside the JSON object.

    Example response: {"ingredients": ["tomato", "onion", "garlic"]}
    """
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
    }

    print(f"Sending image '{image_path}' to OpenRouter for ingredient extraction...")

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
            try:
                ingredients_data = json.loads(assistant_message)
                return ingredients_data.get("ingredients", [])
            except json.JSONDecodeError:
                print("Failed to parse ingredients response as JSON.")
                return []
        else:
            print("No ingredients recognized.")
            return []

    except requests.exceptions.RequestException as e:
        print(f"An API error occurred during ingredient extraction: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred during ingredient extraction: {e}")
        return []


# --- Example Usage (you can run this file directly to test) ---
if __name__ == "__main__":
    test_image_path = "img.png"

    if os.path.exists(test_image_path):
        ingredients = extract_ingredients_from_image(test_image_path)
        if ingredients:
            print("\n--- Detected Ingredients ---")
            for ingredient in ingredients:
                print(f"- {ingredient}")
        else:
            print("\nCould not detect any ingredients.")
    else:
        print(f"Test image not found at '{test_image_path}'. Please create it or update the path.")
