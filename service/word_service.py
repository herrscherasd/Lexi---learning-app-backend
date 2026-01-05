import re
from typing import List

from sqlalchemy.orm import Session

from app.models.words import Word

def process_raw_text(
        *,
        user_id: int,
        raw_text: str,
        db: Session,
) -> List[Word]:
    text = raw_text.lower()

    words = set(re.findall(r"[a-zA-Z]+", text))

    saved_words = []

    for w in words:
        exists = (
            db.query(Word)
            .filter(Word.user_id == user_id, Word.word == w)
            .first()
        )
        if exists:
            continue

        new_word = Word(
            user_id=user_id,
            word=w,
            translation="",
        )

        db.add(new_word)
        saved_words.append(new_word)

    db.commit()

    for w in saved_words:
        db.refresh(w)

    return saved_words

def create_word(
        *,
        user_id: int,
        word: str,
        translation: str,
        db: Session,
        part_of_speech: str | None = None,
        level: str | None = None,
        topic: str | None = None,
        example: str | None = None,
) -> Word:
    new_word = Word(
        user_id=user_id,
        word=word,
        translation=translation,
        part_of_speech=part_of_speech,
        level=level,
        topic=topic,
        example=example,
    )

    db.add(new_word)
    db.commit()
    db.refresh(new_word)

    return new_word

