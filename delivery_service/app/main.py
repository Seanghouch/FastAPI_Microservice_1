import requests
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from contextlib import asynccontextmanager
import os
import consul
from requests import request

from load_env import load_environment

load_environment()

LOCAL_IP = os.environ['LOCAL_IP']
LOCAL_PORT = int(os.environ['LOCAL_PORT'])
CONSUL_IP = os.environ['CONSUL_IP']
CONSUL_PORT = int(os.environ['CONSUL_PORT'])

consul_client = consul.Consul(host=CONSUL_IP, port=CONSUL_PORT)

ORDER_QUEUE = 'order'
PAYMENT_QUEUE = 'payment'

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run at startup
    print("Starting up...")
    register_service(
        service_name="delivery_service",
        service_id="delivery_service_1",
        service_ip=LOCAL_IP,
        service_port=LOCAL_PORT
    )
    yield  # The application runs after this point
    # Code to run at shutdown
    print("Shutting down...")
    unregister_from_consul(service_id='delivery_service_1')

app = FastAPI(lifespan=lifespan)

@app.get('/')
async def default():
    return {'message': 'Welcome to FastAPI'}

@app.post("/delivery/{delivery_id}")
async def get_delivery(delivery_id: int, request: Request):
    return {"delivery_id": delivery_id, "body": await request.body(), "status": "Delivery processed"}

def register_service(service_name: str, service_id: str, service_ip: str, service_port: int):
    """
    Register a service with Consul.
    """
    try:
        service_url = f"http://{service_ip}:{service_port}"
        consul_client.agent.service.register(
            name=service_name,
            service_id=service_id,
            address=service_ip,
            port=service_port,
            http=service_url,
            check=consul.Check.http(f"{service_url}/health", interval="10s", timeout="5s")
        )
        print("Delivery service registered successfully!")
    except Exception as e:
        print(str(e))

@app.post("/order/{order_id}")
async def get_order(order_id: int, request: Request):
    return {"order_id": order_id, "status": "Order processed 2"}

def unregister_from_consul(service_id: str):
    consul_client.agent.service.deregister(service_id)
    print(f'Service_ID: {service_id} deregister')

@app.get("/health")
async def health_check():
    return {"status": "healthy 2"}


if __name__ == '__main__':
    uvicorn.run("main:app", host=LOCAL_IP, port=LOCAL_PORT, reload=True)
