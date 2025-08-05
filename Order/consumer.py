import json
import logging
import pprint
import threading
import pika
from .models import Order, OrderItem

RabbitUser = "user"
RabbitPassword = "password"
logging.basicConfig(level=logging.INFO)




def callback_from_collector(ch, method, properties, body):
    data = json.loads(body)
    logging.info("Received Collector Status - Data: %r" % data)
    try:
        logging.info('Product data successfully processed')
    except Exception as err:
        logging.error(f"Error processing product message: {err}")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def callback_from_courier(ch, method, properties, body):
    data = json.loads(body)
    logging.info("Received Data From Courier: %r" % data)
    try:
        if data.status == 'Cancelled':
            pass


        inactiveTheBasket(data['basket_id'])
        logging.info('Order data successfully processed')
    except Exception as err:
        logging.error(f"Error processing order message: {err}")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_from_rabbitmq(queue, callback):
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='rabbit-container',
        credentials=pika.PlainCredentials(RabbitUser, RabbitPassword),
    ))
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=callback)
    logging.info(f'Consuming from {queue}')
    channel.start_consuming()


def start_consumer():
    queues = {
        'GetStatusFromCollector': callback_from_collector,
        'GetStatusFromCourier': callback_from_courier,
    }

    threads = [
        threading.Thread(target=consume_from_rabbitmq, args=(queue, callback), daemon=True)
        for queue, callback in queues.items()
    ]

    for thread in threads:
        thread.start()

    # Optionally, wait for threads to finish if you need to block the main thread
    # for thread in threads:
    #     thread.join()
