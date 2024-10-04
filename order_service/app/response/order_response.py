from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class OrderResponse(BaseModel):
    order_id: UUID
    item_code: str
    item_description: str
    qty: float
    status: str
    create_at: datetime

    class Config:
        from_attributes = True
