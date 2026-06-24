from pydantic import BaseModel


class UploadResponse(BaseModel):
    total: int = 0
    chunks: int = 0
