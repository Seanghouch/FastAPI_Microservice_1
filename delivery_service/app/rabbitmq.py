import pika
import json

ORDER_QUEUE = 'order'

def notify_user(order_data):
    # Logic to notify the user about the order
    print(f"Notifying user about order: {order_data}")

async def receive_order_message():
    connection_parameters = pika.ConnectionParameters('localhost')
    connection = pika.BlockingConnection(connection_parameters)
    channel = connection.channel()

    # Callback to notify user about the order
    def callback(ch, method, properties, body):
        order_data = json.loads(body)
        notify_user(order_data)
        correlation_id = properties.correlation_id
        # ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f'transaction order: {order_data} with correlation_id: {correlation_id}')

    channel.queue_declare(queue=ORDER_QUEUE)
    channel.basic_consume(queue=ORDER_QUEUE, auto_ack=True, on_message_callback=callback)
    print('Starting Consuming')
    channel.start_consuming()

def start_inventory_consumer():
    connection_parameters = pika.ConnectionParameters('localhost')
    connection = pika.BlockingConnection(connection_parameters)
    channel = connection.channel()

    # Declare the queue for inventory check requests
    channel.queue_declare(queue='inventory_check')

    def callback(ch, method, properties, body):
        message = json.loads(body)
        product_id = message['product_id']
        quantity = message['quantity']

        # Simulate an inventory check
        status = 'available' if quantity <= 1000 else 'unavailable'

        # Send response back to the temporary reply queue
        send_inventory_response(product_id, status, properties.correlation_id, properties.reply_to)

    channel.basic_consume(queue='inventory_check', on_message_callback=callback, auto_ack=True)
    print("Inventory Service: Waiting for inventory check requests...")
    channel.start_consuming()

def send_inventory_response(product_id: int, status: str, correlation_id: str, reply_to: str):
    connection_parameters = pika.ConnectionParameters('localhost')
    connection = pika.BlockingConnection(connection_parameters)
    channel = connection.channel()
    # Send the response to the specific reply_to queue
    response = json.dumps({"product_id": product_id, "status": status})
    channel.basic_publish(exchange='',
                          routing_key=reply_to,
                          body=response,
                          properties=pika.BasicProperties(correlation_id=correlation_id))
    print(response)
    print(f"Waiting for inventory response on {reply_to}")
    connection.close()
