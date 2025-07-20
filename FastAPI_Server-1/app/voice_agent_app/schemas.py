from datetime import datetime
from pydantic import BaseModel


class OrderProcessingSchema(BaseModel):
    id: int
    timestamp: datetime
    transcription: str
    order_details: str
    sizes: str
    toppings: str

    class Config:
        from_attributes = True