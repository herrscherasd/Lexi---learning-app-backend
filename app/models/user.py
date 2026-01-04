from sqlalchemy import Column, Integer, String, DateTime, func

from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    firebase_uid = Column(String, unique=True, index=True, nullable=False)

    email = Column(String, index=True)
    name = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())