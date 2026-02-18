import requests
import json
import base64
import os
from core.config import settings


def recognize_ingredients_from_image(image_path: str) -> list[str]:
    """
    Recognizes ingredients from an image using OpenRouter API.
    """
    try:
        # 1. Encode the local image
        base64_image = encode_image_to_base64(image_path)

        # 2. Prepare the API request payload with the image
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

        # 3. Send the request to the API
        print("Sending request to recognize ingredients...")
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
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

    except FileNotFoundError as e:
        print(f"Error: {e}.")
        return []
    except requests.exceptions.RequestException as e:
        print(f"An API error occurred during ingredient recognition: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred during ingredient recognition: {e}")
        return []


# --- Function to encode the image ---
def encode_image_to_base64(image_path):
    """Encodes an image file to a base64 string."""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found at: {image_path}")
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


# --- Main execution ---
if __name__ == "__main__":
    IMAGE_PATH = 'img.png'
    ingredients = recognize_ingredients_from_image(IMAGE_PATH)
    if ingredients:
        print("\n--- Recognized Ingredients ---")
        print(ingredients)
    else:
        print("\nCould not recognize any ingredients.")
