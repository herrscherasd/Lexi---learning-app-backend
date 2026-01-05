from datetime import datetime
from pydantic import BaseModel

class WordResponse(BaseModel):
    id: int
    word: str
    translation: str
    part_of_speech: str | None
    level: str | None
    topic: str | None
    example: str | None
    strength: float
    created_at: datetime

    class Config:
        from_attributes = True

class WordsProcessRequest(BaseModel):
    raw_text: str