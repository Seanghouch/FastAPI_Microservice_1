from sqlalchemy import Column, Boolean, Integer, Float, String, DateTime
from datetime import datetime
from order_service.app.db.base import Base
from uuid import uuid4


class Order(Base):
    __tablename__ = 'tbl_order'

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, unique=True, nullable=False)
    item_code = Column(String)
    item_description = Column(Integer)
    qty = Column(Float)
    status = Column(String)
    create_at = Column(DateTime, default=datetime.now())

    def __init__(self, order_id=None, **kwargs):
        if order_id is None:
            order_id = str(uuid4())  # Generate a new UUID if not provided
        self.order_id = order_id
        super().__init__(**kwargs)
