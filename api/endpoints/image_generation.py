from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from services import imgGen

router = APIRouter()

class ImagePrompt(BaseModel):
    prompt: str

@router.post("/generate-image/", response_class=Response)
async def generate_image_endpoint(payload: ImagePrompt):
    """
    Generates an image from a text prompt.
    """
    if not payload.prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    try:
        image_bytes = await imgGen.generate_image_from_prompt(payload.prompt)
        return Response(content=image_bytes, media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate image: {str(e)}")

