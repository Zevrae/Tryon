import os
import logging
from google import genai
from core.config import settings

logger = logging.getLogger(__name__)

# Initialize the new SDK client
client = genai.Client(api_key=settings.GEMINI_API_KEY)

# Use the current model built for multimodal image output
MODEL_NAME = "gemini-3.1-flash-image" 

async def generate_tryon_image(person_img_path: str, cloth_img_path: str) -> bytes:
    """
    Sends the person and clothing images to Gemini for virtual try-on using the new SDK.
    """
    person_media = None
    cloth_media = None
    
    try:
        # 1. Upload files using the initialized client
        person_media = client.files.upload(file=person_img_path)
        cloth_media = client.files.upload(file=cloth_img_path)
        print(cloth_media)

        system_prompt = (
            f'''
                I want you to regenerate the image of the person with the same
                {cloth_media} that I have already provided to you.
                Maintain original quality, preserve Face, Pose, Body proportions,Background, 
                Lighting, and Skin tone.
            '''
        )
        
        # 2. Generate content requesting IMAGE modality
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[system_prompt, person_media, cloth_media],
            config=genai.types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            )
        )

        # 3. Extract the image bytes
        for part in response.parts:
            if part.inline_data:
                # inline_data.data contains the raw bytes of the generated image
                return part.inline_data.data
             
        raise Exception("Gemini failed to return an image in the response parts.")

    except Exception as e:
        logger.error(f"Gemini generation failed: {str(e)}")
        raise Exception(f"Gemini image generation failed: {str(e)}")
        
    finally:
        # 4. Cleanup files using the client
        try:
            if person_media:
                client.files.delete(name=person_media.name)
            if cloth_media:
                client.files.delete(name=cloth_media.name)
        except Exception as cleanup_error:
            logger.warning(f"Failed to cleanup Gemini files: {cleanup_error}")