class MockKafkaSchemaRegistry:
    def __init__(self):
        pass

    # noinspection PyUnusedLocal
    @staticmethod
    def get_latest_schema(subject):
        return '{"name": "dummy_schema"}'
