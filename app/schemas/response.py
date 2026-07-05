from pydantic import BaseModel
from typing import Optional

class TryOnResponse(BaseModel):
    success: bool
    image_url: Optional[str] = None
    file_id: Optional[str] = None
    message: str

class ErrorResponse(BaseModel):
    success: bool = False
    message: str