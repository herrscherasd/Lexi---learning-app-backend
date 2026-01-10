import random

from click import prompt
from fastapi import APIRouter, Depends, BackgroundTasks, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List

from app.models.words import Word
from app.schemas.learning import MultipleChoiceAnswer
from dependencies.auth import get_current_user_id
from app.db.deps import get_db


router = APIRouter(
    prefix="/learning",
    tags=["Learning"]
)

@router.get("/multiple-choice")
def get_multiple_choice(
        direction: str = Query("word_to_translation"),
        db: Session = Depends(get_db),
        user_id: int = Depends(get_current_user_id),
):
    word = (
        db.query(Word)
        .filter(
            Word.user_id == user_id,
            Word.status == "ready",
            Word.strength < 1.0,
        )
        .order_by(Word.strength.asc())
        .first()
    )

    if not word:
        raise HTTPException(status_code=404, detail="No words for training")

    if direction == "word_to_translation":
        correct = word.translation
        prompt = word.word
        field = Word.translation
    else:
        correct = word.word
        prompt = word.translation
        field = Word.word

    distractors = (
        db.query(field)
        .filter(
            Word.user_id == user_id,
            field != correct,
        )
        .limit(3)
        .all()
    )

    options = [correct] + [d[0] for d in distractors]
    random.shuffle(options)

    return {
        "word_id": word.id,
        "prompt": prompt,
        "options": options,
    }

@router.post("/multiple-choice/answer")
def answer_multiple_choice(
        payload: MultipleChoiceAnswer,
        db: Session = Depends(get_db),
        user_id: int = Depends(get_current_user_id),
):
    word = (
        db.query(Word)
        .filter(
            Word.id == payload.word_id,
            Word.user_id == user_id,
        )
        .first()
    )

    if not word:
        raise HTTPException(status_code=404, detail="Word not found")

    correct = (
        word.translation
        if payload.direction == "word_to_translation"
        else word.word
    )

    is_correct = payload.selected.strip().lower() == correct.strip().lower()

    if is_correct:
        word.strength = min(word.strength + 0.1, 1.0)
    else:
        word.strength = max(word.strength - 0.2, 0.0)

    db.commit()

    return {
        "correct": is_correct,
        "correct_answer": correct,
        "strength": word.strength,
    }