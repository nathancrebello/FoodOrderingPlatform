from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from datetime import datetime, timezone
from pydantic import BaseModel
from app.settings import Base


class OrderProcessing(Base):
    __tablename__ = 'order_processing'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        nullable=False
    )
    transcription: Mapped[str] = mapped_column(Text, nullable=False)
    order_details: Mapped[str] = mapped_column(Text, nullable=False)


    
class RequestBody(BaseModel):
    text: str  # Replace this with the actual field you expect