from sqlalchemy.orm import Session
from firebase_admin import auth as firebase_auth
from firebase_admin.exceptions import FirebaseError

from core.firebase import initialize_firebase
from app.models.user import User

class AuthenticationError(Exception):
    """Authorization error"""

def authenticate_google(id_token: str, db: Session) -> int:
    initialize_firebase()

    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
    except FirebaseError:
        raise AuthenticationError("Invalid Firebase ID token")

    firebase_uid = decoded_token.get("uid")
    email = decoded_token.get("email")
    name = decoded_token.get("name")

    if not firebase_uid:
        raise AuthenticationError("Firebase ID token is not found")

    user = (
        db.query(User)
        .filter(User.firebase_uid==firebase_uid)
        .first()
    )

    if not user:
        user = User(
            firebase_uid=firebase_uid,
            email=email,
            name=name,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user.id