from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies.auth import get_current_user_id
from app.db.deps import get_db
from app.schemas.user import UserResponse
from service.user_service import get_user_by_id, UserNotFound

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

@router.get("/me", response_model=UserResponse)
def get_me(
        user_id: int  = Depends(get_current_user_id),
        db: Session = Depends(get_db)
):
    try:
        user = get_user_by_id(user_id, db)
    except UserNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user