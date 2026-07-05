from fastapi import UploadFile, HTTPException
from app.core.config import settings

async def validate_image(file: UploadFile) -> None:
    if file.content_type not in settings.SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid format for {file.filename}. Supported formats: jpg, jpeg, png, webp."
        )
    
    # Check file size (Read into memory temporarily to check size)
    file_size = 0
    chunk_size = 1024 * 1024 # 1MB
    
    while chunk := await file.read(chunk_size):
        file_size += len(chunk)
        if file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=400, 
                detail=f"File {file.filename} exceeds the {settings.MAX_FILE_SIZE_MB}MB limit."
            )
    
    await file.seek(0)