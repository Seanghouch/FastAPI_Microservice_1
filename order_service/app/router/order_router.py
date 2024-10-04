import os
from fastapi import APIRouter, HTTPException, status, Header, Request
from fastapi.params import Depends
from sqlalchemy.orm import Session
from order_service.app.db.connection import get_db
from order_service.app.request.order_request import OrderRequest
from order_service.app.service import order_service
from order_service.app.request.list_request import ListRequest
order_router = APIRouter()
from order_service.app.service.consul_service import get_services_from_consul

@order_router.post('/v1/order', tags=['order'])
async def create_order(order: OrderRequest, request: Request, db: Session = Depends(get_db)):
    header = request.headers
    # check method and header allowed
    check_header(header)
    if header['action'] == 'show':
        # raise HTTPException(status_code=404, detail=f"action {header['action']}: not yet implement")
        return await order_service.show_order(db)
    if header['action'] == 'save':
        # raise HTTPException(status_code=404, detail=f"action {header['action']}: not yet implement")
        return await order_service.create_order(order, db)
    if header['action'] == 'update':
        raise HTTPException(status_code=404, detail=f"action {header['action']}: not yet implement")
    if header['action'] == 'delete':
        raise HTTPException(status_code=404, detail=f"action {header['action']}: not yet implement")


@order_router.post('/v1/order/get_order')
async def get_order(request: ListRequest, db: Session = Depends(get_db)):
    abc = await get_services_from_consul()
    print(abc)
    return await order_service.show_order(request, db)


def check_header(header):
    # check has action in header
    if 'action' not in header:
        raise HTTPException(status_code=405, detail=f"Missing 'action' in header.")
    # check action has values, show, save, update, delete only
    if header['action'] not in ['show', 'save', 'update', 'delete']:
        raise HTTPException(status_code=405, detail=f"Your action: {header['action']} not allowed.")
