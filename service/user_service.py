from sqlalchemy.orm import Session

from app.models.user import User

class UserNotFound(Exception):
    pass

def get_user_by_id(user_id: int, db: Session) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UserNotFound()
    return user