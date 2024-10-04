import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
from load_env import load_environment
import pika
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import requests

load_environment()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run at startup
    print("Starting up...")
    yield  # The application runs after this point
    # Code to run at shutdown
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost,https://example.com").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a Consul client
CONSUL_URL = os.environ['CONSUL_URL']

@app.get('/')
async def home():
    return {'message': 'Welcome to FastAPI'}

@app.api_route("/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"], include_in_schema=False)
async def proxy_request(service_name: str, path: str, request: Request):
    services = get_services_from_consul(CONSUL_URL)
    if service_name not in services:
        return JSONResponse(status_code=404, content={"detail": f"Service: {service_name} not found"})
    service_url = f"{services[service_name]}/{path}"
    # Extract method and forward request to the service
    method = request.method
    service_path = f"{service_url}/{path}"
    # Extract headers and body from the incoming request
    headers = dict(request.headers)
    param = request.query_params
    body = await request.body()
    data = {
        'Server': service_path,
        'Header': headers,
        'Method': method,
        'Param': param,
        'body': body
    }
    # Forward request based on HTTP method
    # if method == "GET":
    #     response = f"'server':{service_path}, 'Header': {headers}, 'Method': {method}, 'Param': {param}"
    # elif method == "POST":
    #     response = f"'server':{service_path}, 'Header': {headers}, 'Method': {method}, 'body': {body}"
    # elif method == "PUT":
    #     response = f"'server':{service_path}, 'Header': {headers}, 'Method': {method}, 'body': {body}"
    # elif method == "DELETE":
    #     response = f"'server':{service_path}, 'Header': {headers}, 'Method': {method}, 'body': {body}"
    # else:
    #     raise HTTPException(status_code=405, detail=f"Method {method} not allowed")

    if method not in ['POST']:
        raise HTTPException(status_code=405, detail=f"Method {method} not allowed")
    else:
        if 'action' not in headers:
            raise HTTPException(status_code=405, detail=f"Missing 'action' in Header.")

        if headers['action'] not in ['show', 'save', 'update', 'delete']:
            raise HTTPException(status_code=405, detail=f"Your action: {headers['action']} not allowed.")
            # raise HTTPException(status_code=200, detail=f"Your action: {headers['action']} allowed.")
        async with httpx.AsyncClient() as client:
            response = await client.request(
                request.method,
                service_url,
                headers=request.headers,
                data=await request.body()
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)


def get_services_from_consul(consul_url):
    # Query Consul for the list of services
    try:
        response = requests.get(f"{consul_url}/v1/catalog/services")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=404, detail='Consul Service not found.')
    services = response.json()
    service_dict = {}

    for service_name in services.keys():
        # Query Consul for service instances
        service_instances_response = requests.get(f"{consul_url}/v1/catalog/service/{service_name}")
        service_instances_response.raise_for_status()

        instances = service_instances_response.json()
        # Use the first instance's address and port
        if instances:
            service_address = instances[0]['ServiceAddress']
            service_port = instances[0]['ServicePort']
            service_dict[service_name] = f"http://{service_address}:{service_port}"

    return service_dict

def publish_order(order_id: int):

    connection_parameters = pika.ConnectionParameters('localhost')
    connection = pika.BlockingConnection(connection_parameters)
    channel = connection.channel()
    channel.queue_declare(queue='order_queue')
    channel.basic_publish(exchange='', routing_key='order_queue', body=str(order_id))
    connection.close()

if __name__ == '__main__':
    uvicorn.run("main:app", host='localhost', port=8000, reload=True)
