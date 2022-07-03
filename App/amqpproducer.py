import pika, json
import os


class SignalProducer:
    def __init__(self, channel_name):
        self.url = os.environ.get('AMQP_KEY')
        self.channel = self.connection.channel()
        self.channel_name = channel_name

    def produce_event(self, method, body):
        properties = pika.BasicProperties(
            method
        )
        self.channel.basic_publish(
            'worker',
            routing_key=self.channel_name,
            body= b'hello World',
            properties=properties
        )
