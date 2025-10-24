import uuid


class MockKafkaProducer:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.topics = {}

    def reset(self):
        self.topics = {}

    # noinspection PyUnusedLocal
    def produce(self, topic, key_schema, value_schema, key, value):
        if topic not in self.topics:
            self.topics[topic] = []
        self.topics[topic].append({'key': key, 'value': value})

    def flush(self):
        pass

    def get(self, topic):
        return self.topics[topic] if topic in self.topics else []
