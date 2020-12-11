import json
import os

import pika

from .config import RABBIT_CONFIG
from .telegram import send_message


class RabbitMQWorker:
    """Class for wrap rabbit
    :attr callback: queue callback
    :attr from_queue: listen queue
    :attr to_queue: next queue
    """

    def __init__(self, callback=None, from_queue=None, to_queue=None):
        self.custom_callback = callback
        self.from_queue = from_queue
        self.to_queue = to_queue
        self.channel = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBIT_CONFIG['host'], heartbeat=RABBIT_CONFIG['heartbeat'])
        ).channel()

    def send(self, message):
        """Sent task in queue
        :param message: task massage
        """
        self.channel.basic_publish(exchange='', routing_key=self.to_queue, body=json.dumps(message))

    def listen_queue(self):
        """Run rabbit worker"""
        if self.from_queue:
            self.channel.queue_declare(queue=self.from_queue, durable=True)
        if self.to_queue:
            self.channel.queue_declare(queue=self.to_queue, durable=True)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.from_queue, on_message_callback=self.callback)
        self.channel.start_consuming()

    def callback(self, channel, method_frame, _, body):
        """Callback for rabbit task
        :param channel: rabbit channel
        :param method_frame: rabbit method
        :param _: rabbit properties
        :param body: task body
        """
        try:
            message = json.loads(body)
            message = self.custom_callback(message)
            if self.to_queue:
                self.send(message)
        except Exception as e:
            print(e)
            send_message(str(e), os.environ.get('ADMIN_CHANNEL'))
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)
