import regex as re
from typing import List

from sqlalchemy.orm import Session

from app.models.words import Word
from app.db.session import SessionLocal
from service.ai_service import enrich_words

COMMON_PHRASES = {
    "güle güle",
    "ne haber",
    "iyi günler",
    "iyi akşamlar",
    "hoş geldin",
    "hoşça kal",
}

def extract_candidates(text: str) -> set[str]:
    text = text.lower()

    tokens = re.findall(r"\p{L}+", text)

    candidates: set[str] = set(tokens)

    for i in range(len(tokens) - 1):
        w1, w2 = tokens[i], tokens[i + 1]

        if w1 == w2:
            candidates.add(f"{w1} {w2}")
            continue

        phrase = f"{w1} {w2}"
        if phrase in COMMON_PHRASES:
            candidates.add(phrase)

    return candidates

def process_raw_text(
        *,
        user_id: int,
        raw_text: str,
        db: Session,
) -> List[Word]:

    candidates = extract_candidates(raw_text)

    saved_words: List[Word] = []

    for item in candidates:
        if len(item) < 2:
            continue

        exists = (
            db.query(Word)
            .filter(
                Word.user_id == user_id,
                Word.word == item,
            )
            .first()
        )

        if exists:
            continue

        new_word = Word(
            user_id=user_id,
            word=item,
            translation="",
            status="pending",
            strength=0.0,
        )

        db.add(new_word)
        saved_words.append(new_word)

    db.commit()

    for w in saved_words:
        db.refresh(w)

    return saved_words

def chunked(lst: list[str], size: int):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

async def enrich_and_update_words(
        *,
        user_id: int,
        words: list[str],
):
    db = SessionLocal()

    try:
        ai_results = await enrich_words(words)

        for item in ai_results:
            word = (
                db.query(Word)
                .filter(
                    Word.user_id == user_id,
                    Word.word == item["word"],
                )
                .first()
            )
            if not word:
                continue

            word.translation = item["translation"]
            word.part_of_speech = item["part_of_speech"]
            word.level = item["level"]
            word.topic = item["topic"]
            word.example = item["example"]

            word.status = "ready"

        db.commit()

    except Exception as exc:
        print("🔥 AI BACKGROUND ERROR:", exc)
        db.query(Word) \
            .filter(Word.user_id == user_id, Word.word.in_(words)) \
            .update({"status": "failed"}, synchronize_session=False)

        db.commit()

    finally:
        db.close()