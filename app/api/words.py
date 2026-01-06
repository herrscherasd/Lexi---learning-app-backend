from fastapi import APIRouter, Depends, BackgroundTasks, Query
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