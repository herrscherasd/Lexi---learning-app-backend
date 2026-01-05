from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Float, func
from sqlalchemy.orm import relationship

from app.db.base import Base

class Word(Base):
    __tablename__ = 'words'

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True)

    word = Column(String, nullable=False, index=True)
    translation = Column(String, nullable=False)

    part_of_speech = Column(String)
    level = Column(String)
    topic = Column(String)

    example = Column(String)

    strength = Column(Float, default=0.0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="words")