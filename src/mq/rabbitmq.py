import traceback
from time import sleep

import pika

from src.config import get_config

def callback(channel, method, properties, body):
    print(f"메시지 수신됨: {body.decode()}")


def get_rabbitmq_connection():
    config = get_config()['mq']['rabbitmq']
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=config['host'],
            port=config['port'],
            virtual_host=config['vhost'],
            credentials=pika.PlainCredentials(
                username=config['user'],
                password=config['pass'],
            ),
        )
    )
    channel = connection.channel()
    return connection, channel

def keep_consuming(mqchannel):
    def inner_method():
        while True:
            try:
                mqchannel.queue_declare(queue='node.TEST01', durable=True)
                mqchannel.basic_consume(
                    queue='node.TEST01',
                    on_message_callback=callback,
                    auto_ack=True
                )
                mqchannel.start_consuming()
            except Exception as e:
                traceback.print_exc()
                sleep(10)

    return inner_method