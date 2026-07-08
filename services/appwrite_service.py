from appwrite.client import Client
from appwrite.services.storage import Storage
from appwrite.input_file import InputFile
from appwrite.id import ID
from core.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Appwrite client
client = Client()
client.set_endpoint(settings.APPWRITE_ENDPOINT)
client.set_project(settings.APPWRITE_PROJECT_ID)
client.set_key(settings.APPWRITE_API_KEY)

storage = Storage(client)

async def upload_generated_image(file_path: str, filename: str = "generated-tryon.png") -> dict:
    """
    Uploads an image to Appwrite storage and returns the file ID and public URL.
    """
    try:
        result = storage.create_file(
            bucket_id=settings.APPWRITE_BUCKET_ID,
            file_id=ID.unique(),
            file=InputFile.from_path(file_path),
            permissions=["read(\"any\")"]  # Public read
        )
        
        # ✅ CORRECT: Use dot notation to access the ID on the File object
        file_id = result.id
        
        # Generate the public URL
        url = f"{settings.APPWRITE_ENDPOINT}/storage/buckets/{settings.APPWRITE_BUCKET_ID}/files/{file_id}/view?project={settings.APPWRITE_PROJECT_ID}"
        
        return {
            "file_id": file_id,
            "url": url
        }
    except Exception as e:
        logger.error(f"Appwrite upload failed: {str(e)}")
        raise Exception("Failed to upload image to Appwrite.")