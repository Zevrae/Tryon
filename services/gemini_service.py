import asyncio
import logging
from typing import List
from google import genai
from core.config import settings

logger = logging.getLogger(__name__)

client = genai.Client(api_key=settings.GEMINI_API_KEY)
MODEL_NAME = "gemini-3.1-flash-lite-image"

async def generate_tryon_image(person_img_path: str, cloth_img_paths: List[str]) -> bytes:
    """
    Sends the person image and one or more clothing images to Gemini for a
    virtual try-on that composites every garment onto the same person.
    """
    try:
        return await asyncio.wait_for(
            _generate_tryon_image_inner(person_img_path, cloth_img_paths),
            timeout=settings.GEMINI_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        logger.error(
            f"Gemini generation timed out after {settings.GEMINI_TIMEOUT_SECONDS}s"
        )
        raise Exception(
            f"Gemini image generation timed out after {settings.GEMINI_TIMEOUT_SECONDS}s"
        )


async def _generate_tryon_image_inner(person_img_path: str, cloth_img_paths: List[str]) -> bytes:
    person_media = None
    cloth_media_list = []

    try:
        # Uploads were previously sequential (person, then each garment one
        # at a time) — with several garments that's N+1 network round trips
        # stacked end to end. Uploading concurrently means wall-clock time
        # is roughly one round trip, not N+1 of them.
        person_media, *cloth_media_list = await asyncio.gather(
            client.aio.files.upload(file=person_img_path),
            *[client.aio.files.upload(file=p) for p in cloth_img_paths],
        )

        garment_count_note = (
            "I have provided one clothing item to try on."
            if len(cloth_media_list) == 1
            else f"I have provided {len(cloth_media_list)} clothing items to try on together, "
            "as a single coordinated outfit (e.g. top, bottom, accessories)."
        )

        system_prompt = f"""
            I want you to regenerate the image of the person wearing the
            clothing item(s) that I have already provided to you. {garment_count_note}
            Maintain original quality, preserve Face, Pose, Body proportions, Background,
            Lighting, and Skin tone.
        """

        # Use await client.aio for async generation
        response = await client.aio.models.generate_content(
            model=MODEL_NAME,
            contents=[system_prompt, person_media, *cloth_media_list],
            config=genai.types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            ),
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
        # Use await client.aio for async cleanup
        try:
            if person_media:
                await client.aio.files.delete(name=person_media.name)
            for cloth_media in cloth_media_list:
                await client.aio.files.delete(name=cloth_media.name)
        except Exception as cleanup_error:
            logger.warning(f"Failed to cleanup Gemini files: {cleanup_error}")
