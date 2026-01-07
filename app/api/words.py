from fastapi import APIRouter, Depends, BackgroundTasks, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List

from app.models.words import Word
from dependencies.auth import get_current_user_id
from app.db.deps import get_db
from app.schemas.word import WordsProcessRequest, WordResponse
from service.word_service import process_raw_text, enrich_and_update_words, chunked

MAX_WORDS = 8

router = APIRouter(
    prefix="/words",
    tags=["Words"],
)

@router.get("", response_model=List[WordResponse])
def get_words(
    status: str | None = Query(default=None),
    topic: str | None = Query(default=None),
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    query = db.query(Word).filter(Word.user_id == user_id)

    if status:
        query = query.filter(Word.status == status)

    if topic:
        query = query.filter(Word.topic == topic)

    if search:
        query = query.filter(
            or_(
                Word.word.ilike(f"%{search}%"),
                Word.translation.ilike(f"%{search}%"),
                Word.example.ilike(f"%{search}%"),
            )
        )

    return query.order_by(Word.created_at.desc()).all()

@router.post("/process", response_model=List[WordResponse],)
def process_words(
        payload: WordsProcessRequest,
        background_tasks: BackgroundTasks,
        user_id: int = Depends((get_current_user_id)),
        db: Session = Depends(get_db),
):
    words = process_raw_text(
        user_id=user_id,
        raw_text=payload.raw_text,
        db=db,
    )

    all_words = [w.word for w in words]

    for batch in chunked(all_words, MAX_WORDS):
        background_tasks.add_task(
            enrich_and_update_words,
            user_id=user_id,
            words=batch,
        )

    return words

@router.post("/retry", response_model=WordResponse)
def retry_failed_words(
    background_tasks: BackgroundTasks,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    failed_words = (
        db.query(Word)
        .filter(
            Word.user_id == user_id,
            Word.status == "failed",
        )
        .all()
    )

    if not failed_words:
        return []

    words_list = [w.word for w in failed_words]

    for batch in chunked(words_list, MAX_WORDS):
        background_tasks.add_task(
            enrich_and_update_words,
            user_id=user_id,
            words=batch,
        )

    return failed_words

@router.post("/{word_id}/answer", response_model=WordResponse)
def answer_word(
        word_id: int,
        correct: bool = Query(...),
        user_id: int = Depends(get_current_user_id),
        db: Session = Depends(get_db),
):
    word = (
        db.query(Word)
        .filter(
            Word.user_id == user_id,
            Word.id == word_id,
        )
        .first()
    )

    if not word:
        raise HTTPException(
            status_code=404,
            detail="Word not found",
        )

    if correct:
        word.strength += 0.2
    else:
        word.strength -= 0.3

    word.strength = max(0.0, min(word.strength, 1.0))

    db.commit()
    db.refresh(word)

    return word

@router.get("/flashcards", response_model=List[WordResponse])
def get_flashcards(
        limit: int = Query(default=10, ge=1, le=30),
        db: Session = Depends(get_db),
        user_id: int = Depends(get_current_user_id),
):
    return (
        db.query(Word)
        .filter(
            Word.user_id == user_id,
            Word.status == "ready",
            Word.strength < 0.4,
        )
        .order_by(Word.created_at.asc())
        .limit(limit)
        .all()
    )