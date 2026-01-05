from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from dependencies.auth import get_current_user_id
from app.db.deps import get_db
from app.schemas.word import WordsProcessRequest, WordResponse
from service.word_service import process_raw_text, enrich_and_update_words

router = APIRouter(
    prefix="/words",
    tags=["Words"],
)

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

    background_tasks.add_task(
        enrich_and_update_words,
        user_id=user_id,
        words=[w.word for w in words],
    )

    return words