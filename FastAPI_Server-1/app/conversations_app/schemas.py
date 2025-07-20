from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import pytz
from enum import Enum
from app.users_app.schemas import UserSchema

class OrderOutput(BaseModel):
    order_details: str = Field(
        ...,
        description="Comma-separated list of items with quantities",
        example="1 x *item A in menu*, 1 x *item B in menu*, 1 x *item C in menu*"
    )
    sizes: str = Field(
        ...,
        description="Corresponding sizes for each item in order_details",
        example="sizes: 1 x One Size Option, 1 x Small, 1 x Large, 1 x Medium, 1 x ?, 1 x !"
    )
    toppings: str = Field(
        ...,
        description="Corresponding toppings for each item in order_details",
        example="sizes:  1 x No Topping Option, 1 x *Topping X in menu*, 1 x ?, 1 x !"
    )


class ConversationBase(BaseModel):
    conversation_id: str = Field(..., description="Unique identifier for a conversation.", max_length=100)
    chunk: Optional[str] = Field(None, description="The current chunk of the conversation.")
    context: str = Field(..., description="Contextual information including previous chunks and order state.")
    inferred_command: Optional[str] = Field(None, description="Inferred command")
    ideal_inference: Optional[str] = Field(None, description="Ideal inference for comparison.")

class ConversationSchema(ConversationBase):
    id: int
    timestamp: datetime
    initial_review_by: Optional[int] = None
    final_review_by: Optional[int] = None

    @field_validator('timestamp')
    @classmethod
    def convert_to_ist(cls, v: datetime) -> datetime:
        if v is not None:
            return v.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata'))
        return v

    class Config:
        from_attributes = True

class CreateConversationSchema(ConversationBase):
    initial_review_by_id: Optional[int] = None
    final_review_by_id: Optional[int] = None

    class Config:
        from_attributes = True

class UpdateConversationSchema(BaseModel):
    chunk: Optional[str] = None
    context: Optional[str] = None
    inferred_command: Optional[str] = None
    ideal_inference: Optional[str] = None
    initial_review_by_id: Optional[int] = None
    final_review_by_id: Optional[int] = None

    class Config:
        from_attributes = True