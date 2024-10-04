from pydantic import BaseModel
from uuid import UUID


class OrderRequest(BaseModel):
    order_id: UUID = None
    item_code: str
    item_description: str
    qty: float
    status: str
