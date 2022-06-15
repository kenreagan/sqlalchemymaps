import pika, json


class SignalProducer:
    def __init__(self, channel_name):
        self.connection = pika.BlockingConnection()
        self.channel = self.connection.channel()
        self.channel_name = channel_name

    def produce_event(self, method, body):
        properties = pika.BasicProperties(
            method
        )
        self.channel.basic_publish(
            '',
            routing_key=self.channel_name,
            body=json.dumps(body, ensure_ascii=True),
            properties=properties
        )
