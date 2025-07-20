from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from app.settings import Base
from datetime import datetime, timezone
from app.users_app.models import UserModel
from pydantic import BaseModel

class RequestBody(BaseModel):
    text: str  # Replace this with the actual field you expect

class Conversation(Base):
    __tablename__ = 'conversations'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    conversation_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        nullable=False
    )
    chunk: Mapped[str] = mapped_column(Text, nullable=True)
    context: Mapped[str] = mapped_column(Text, nullable=False)
    inferred_command: Mapped[str] = mapped_column(Text, nullable=True)
    ideal_inference: Mapped[str] = mapped_column(Text, nullable=True)
    initial_review_by: Mapped[int | None] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    final_review_by: Mapped[int | None] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    # Relationships
    initial_reviewer = relationship("UserModel", foreign_keys=[initial_review_by])
    final_reviewer = relationship("UserModel", foreign_keys=[final_review_by])