from pydantic import BaseModel
from typing import Literal

class MultipleChoiceAnswer(BaseModel):
    word_id: int
    selected: str
    direction: Literal["word_to_translation", "translation_to_word"]