from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services import imgGen
from typing import Dict

router = APIRouter()

class ImagePrompt(BaseModel):
    prompt: str

class ImageResponse(BaseModel):
    url: str
    public_id: str

@router.post("/generate-image/", response_model=ImageResponse)
async def generate_image_endpoint(payload: ImagePrompt):
    """
    Generates an image from a text prompt, uploads it to Cloudinary,
    and returns the image URL and public ID.
    """
    if not payload.prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    try:
        upload_result = await imgGen.generate_image_from_prompt(payload.prompt)

        if not upload_result or "secure_url" not in upload_result or "public_id" not in upload_result:
            raise HTTPException(status_code=500, detail="Failed to get upload result from Cloudinary.")

        return ImageResponse(
            url=upload_result["secure_url"],
            public_id=upload_result["public_id"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate image: {str(e)}")
