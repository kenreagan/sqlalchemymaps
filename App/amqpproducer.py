import pika, json


class SignalProducer:
    def __init__(self, channel_name):
        self.url = 'amqps://zihhojzz:FFw4QOF6kVqu39ux1klMs8won5ww2ynU@albatross.rmq.cloudamqp.com/zihhojzz'
        self.connection = pika.BlockingConnection()
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
