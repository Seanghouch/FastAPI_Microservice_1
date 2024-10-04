from fastapi.exceptions import HTTPException
import pika
import json


def push_message(order_id: int, correlation_id: str):

    connection_parameters = pika.ConnectionParameters(host='localhost', port=5672)
    connection = pika.BlockingConnection(connection_parameters)
    channel = connection.channel()

    channel.queue_declare(queue='order')
    message = str(order_id)
    channel.basic_publish(
                        exchange='',
                        routing_key='order',
                        body=message,
                        properties=pika.BasicProperties(correlation_id=correlation_id, reply_to=''),
                    )
    print(f'send message: {message} with correlation_id: {correlation_id}')
    # for i in range(10):
    #     message = f'transaction... {i}'
    #     channel.basic_publish(exchange='', routing_key='letterbox', body=message)
    #     print(f'send message: {message}')

    connection.close()

async def send_inventory_check(product_id: int, quantity: int, order_id: int, correlation_id: str):
    try:
        connection_parameters = pika.ConnectionParameters('localhost')
        connection = pika.BlockingConnection(connection_parameters)
        channel = connection.channel()
        response = None
        # Create a temporary exclusive reply queue
        result = channel.queue_declare(queue='', exclusive=True)
        reply_queue = result.method.queue

        # Generate a unique correlation ID
        correlation_id = correlation_id

        # Send the inventory check request to the Inventory Service
        message = json.dumps({"product_id": product_id, "quantity": quantity, 'order_id': order_id, 'correlation_id': correlation_id})

        channel.basic_publish(exchange='',
                              routing_key='inventory_check',
                              body=message,
                              properties=pika.BasicProperties(
                                  reply_to=reply_queue,
                                  correlation_id=correlation_id))
        print(message)

        result = await wait_for_inventory_response(connection, reply_queue, correlation_id)

        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=f'service not found.')

async def wait_for_inventory_response(connection, reply_queue, correlation_id):
    response = None
    try:
        def callback(ch, method, properties, body):
            nonlocal response
            if properties.correlation_id == correlation_id:
                response = json.loads(body)
                connection.close()

        channel = connection.channel()
        channel.basic_consume(queue=reply_queue, on_message_callback=callback, auto_ack=True)

        # Start consuming the message
        print(f"Waiting for inventory response on {reply_queue}")
        while response is None:
            connection.process_data_events()
        return response
    except Exception as e:
        raise HTTPException(status_code=404, detail=f'service not found.')
