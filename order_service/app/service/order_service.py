from sqlalchemy.orm import Session
from order_service.app.request.order_request import OrderRequest
from order_service.app.repo import order_repo
from order_service.app.response.data_response import ResponseData, ResponseDataList
from order_service.app.request.list_request import ListRequest


async def create_order(order: OrderRequest, db: Session):
    data = await order_repo.create_order(order, db)
    result = ResponseData(code=200, message='Order has been created successfully.', data=data)
    return result

async def show_order(request: ListRequest, db: Session):
    data = await order_repo.show_order(request, db)
    total_record = len(data)
    result = ResponseDataList(code=200, message='Get data successfully.', total_record=total_record, data=data)
    return result
