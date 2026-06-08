from pydantic import BaseModel


class ProcessResponse(BaseModel):
    total: int = 0
    ok: int = 0
    fail: int = 0