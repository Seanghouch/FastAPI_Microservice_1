from fastapi import HTTPException

from sqlalchemy.orm import Session
from order_service.app.request import order_request
from order_service.app.response.order_response import OrderResponse
from order_service.app.model import order_model
from order_service.app.request.list_request import ListRequest
from order_service.app.service.filter_specification import dynamic_search
from uuid import uuid4


async def create_order(order: order_request, db: Session):
    try:
        db_order = order_model.Order(**order.dict())
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        data = OrderResponse.model_validate(db_order)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

async def show_order(request: ListRequest, db: Session):
    db_order = dynamic_search(db=db, table_name=order_model.Order.__tablename__, request=request)
    data = list(map(OrderResponse.model_validate, db_order))
    return data


