import json
import logging
from pprint import pprint

import pika

RabbitUsername = "user"
RabbitPassword = "password"
logging.basicConfig(level=logging.INFO)


def SendToProducer(data, queue) -> None:
    try:

        connection = pika.BlockingConnection(
            pika.ConnectionParameters('rabbit-container',
            credentials=pika.PlainCredentials(RabbitUsername, RabbitPassword)
                                      )
        )

        channel = connection.channel()
        channel.queue_declare(queue=queue, durable=True, auto_delete=False)

        channel.basic_publish(exchange='',
                              routing_key=queue,
                              body=json.dumps(data),
                              properties=pika.BasicProperties(
                                  delivery_mode=2,
                                  )
                              )

        logging.info('[x] Message Sent to RabbitMQ data : %r' % data)
        connection.close()
    except Exception as e:
        logging.error('[x] Exception occurred: %s' % e)




