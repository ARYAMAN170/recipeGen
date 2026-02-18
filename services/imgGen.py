# pip install 'fireworks-ai'
import fireworks.client
from fireworks.client.image import ImageInference, Answer
import io
from core.config import settings
import cloudinary
import cloudinary.uploader

# Configure Cloudinary
cloudinary.config(
  cloud_name = settings.CLOUD_NAME,
  api_key = settings.CLOUD_API_KEY,
  api_secret = settings.CLOUD_API_SECRET
)

# Initialize the ImageInference client
fireworks.client.api_key = settings.FIREWORKS_API_KEY
inference_client = ImageInference(model="stable-diffusion-xl-1024-v1-0")

async def generate_image_from_prompt(prompt: str) -> dict:
    """
    Generates an image from a text prompt using Fireworks AI and uploads it to Cloudinary.
    """
    # Generate an image using the text_to_image method
    answer : Answer = await inference_client.text_to_image_async(
        prompt=prompt,
        #cfg_scale=undefined,
        height=1024,
        width=1024,
        sampler=None,
        # steps=undefined,
        seed=0,
        safety_check=False,
        output_image_format="JPG",
        # Add additional parameters here
    )

    if answer.image is None:
        raise RuntimeError(f"No return image, {answer.finish_reason}")

    byte_arr = io.BytesIO()
    answer.image.save(byte_arr, format='JPEG')
    image_bytes = byte_arr.getvalue()

    try:
        # Upload the image to Cloudinary
        upload_result = cloudinary.uploader.upload(image_bytes)
        return upload_result
    except Exception as e:
        print(f"Cloudinary upload failed: {e}")
        raise RuntimeError(f"Failed to upload image to Cloudinary: {e}")
