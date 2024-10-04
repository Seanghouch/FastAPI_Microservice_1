import os
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from load_env import load_environment
from order_service.app.service.consul_service import register_service, unregister_from_consul
from router import order_router
from order_service.app.db import base, connection

load_environment()

LOCAL_IP = os.environ['LOCAL_IP']
LOCAL_PORT = int(os.environ['LOCAL_PORT'])
CONSUL_IP = os.environ['CONSUL_IP']
CONSUL_PORT = int(os.environ['CONSUL_PORT'])

# create the database table
base.Base.metadata.create_all(bind=connection.engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run at startup
    print("Starting up...")
    register_service(
        service_name="order_service",
        service_id="order_service_1",
        service_ip=LOCAL_IP,
        service_port=LOCAL_PORT
    )
    yield  # The application runs after this point
    # Code to run at shutdown
    print("Shutting down...")
    unregister_from_consul(service_id='order_service_1')

app = FastAPI(lifespan=lifespan)

app.include_router(order_router.order_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == '__main__':
    uvicorn.run("main:app", host=LOCAL_IP, port=LOCAL_PORT, reload=True)
