from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from requests import Session

from app.db.deps import get_db
from service.auth_service import authenticate_google, AuthenticationError
from core.jwt import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

class GoogleAuthRequest(BaseModel):
    id_token: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post(
    "/google",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
)
def google_auth(payload: GoogleAuthRequest, db: Session = Depends(get_db)):
    try:
        user_id = authenticate_google(payload.id_token, db)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )

    token = create_access_token(user_id)
    return AuthResponse(access_token=token)
