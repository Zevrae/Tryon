import os
import tempfile
import aiofiles
from fastapi import UploadFile

async def save_temp_upload(file: UploadFile) -> str:
    """Saves an UploadFile to a temporary directory and returns the path."""
    _, ext = os.path.splitext(file.filename)
    fd, path = tempfile.mkstemp(suffix=ext)
    os.close(fd)
    
    async with aiofiles.open(path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
        
    return path

async def save_temp_bytes(image_bytes: bytes, ext: str = ".png") -> str:
    """Saves raw bytes to a temporary file and returns the path."""
    fd, path = tempfile.mkstemp(suffix=ext)
    os.close(fd)
    
    async with aiofiles.open(path, 'wb') as out_file:
        await out_file.write(image_bytes)
        
    return path

def cleanup_temp_files(*file_paths: str):
    """Deletes temporary files."""
    for path in file_paths:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass