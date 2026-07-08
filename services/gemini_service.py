import os
import logging
from google import genai
from core.config import settings

logger = logging.getLogger(__name__)

client = genai.Client(api_key=settings.GEMINI_API_KEY)
MODEL_NAME = "gemini-3.1-flash-lite-image" 

async def generate_tryon_image(person_img_path: str, cloth_img_path: str) -> bytes:
    """
    Sends the person and clothing images to Gemini for virtual try-on using the new SDK.
    """
    person_media = None
    cloth_media = None
    
    try:
        # ✅ Use await client.aio for async file uploads
        person_media = await client.aio.files.upload(file=person_img_path)
        cloth_media = await client.aio.files.upload(file=cloth_img_path)

        # ✅ Use plain text (no f-string or object interpolation needed)
        system_prompt = """
            I want you to regenerate the image of the person with the same
            clothing that I have already provided to you.
            Maintain original quality, preserve Face, Pose, Body proportions, Background, 
            Lighting, and Skin tone.
        """
        
        # ✅ Use await client.aio for async generation
        response = await client.aio.models.generate_content(
            model=MODEL_NAME,
            contents=[system_prompt, person_media, cloth_media],
            config=genai.types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            )
        )

        # Extract the image bytes
        for part in response.parts:
            if part.inline_data:
                return part.inline_data.data
                 
        raise Exception("Gemini failed to return an image in the response parts.")

    except Exception as e:
        logger.error(f"Gemini generation failed: {str(e)}")
        raise Exception(f"Gemini image generation failed: {str(e)}")
        
    finally:
        # ✅ Use await client.aio for async cleanup
        try:
            if person_media:
                await client.aio.files.delete(name=person_media.name)
            if cloth_media:
                await client.aio.files.delete(name=cloth_media.name)
        except Exception as cleanup_error:
            logger.warning(f"Failed to cleanup Gemini files: {cleanup_error}")