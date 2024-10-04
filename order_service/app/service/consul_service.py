import os
import consul
import requests
from fastapi import HTTPException
from order_service.app.load_env import load_environment
import httpx

load_environment()

LOCAL_IP = os.environ['LOCAL_IP']
LOCAL_PORT = int(os.environ['LOCAL_PORT'])
CONSUL_IP = os.environ['CONSUL_IP']
CONSUL_PORT = int(os.environ['CONSUL_PORT'])
consul_client = consul.Consul(host=CONSUL_IP, port=CONSUL_PORT)


async def get_services_from_consul():
    consul_url = os.environ['CONSUL_URL']

    async with httpx.AsyncClient() as client:
        try:
            # Query Consul for the list of services
            response = await client.get(f"{consul_url}/v1/catalog/services")
            response.raise_for_status()
            services = response.json()
        except httpx.HTTPStatusError:
            raise HTTPException(status_code=404, detail='Consul Service not found.')

        service_dict = {}
        print(services)
        # Querying for each service's instances
        for service_name in services.keys():
            try:
                service_instances_response = await client.get(f"{consul_url}/v1/catalog/service/{service_name}")
                service_instances_response.raise_for_status()

                instances = service_instances_response.json()

                # Use the first instance's address and port
                if instances:
                    service_address = instances[0]['ServiceAddress']
                    service_port = instances[0]['ServicePort']
                    service_dict[service_name] = f"http://{service_address}:{service_port}"

            except httpx.HTTPStatusError:
                continue  # Skipping failed service lookups
    return service_dict


def unregister_from_consul(service_id: str):
    consul_client.agent.service.deregister(service_id)
    print(f'Service_ID: {service_id} deregister.')


def register_service(service_name: str, service_id: str, service_ip: str, service_port: int):
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
        print("Order service registered successfully!")
    except Exception as e:
        print(str(e))
