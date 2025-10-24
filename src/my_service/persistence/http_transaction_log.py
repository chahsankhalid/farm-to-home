from <%my_service%>.domain.models.http_transaction import HttpTransaction
from <%my_service%>.persistence.kafka_streaming import kafka_streaming

KAFKA_TOPIC = 'fct.bronze.http-transactions.v0'


def save_http_transaction(http_transaction: HttpTransaction):
    key = http_transaction.kafka_key()
    value = http_transaction.kafka_value()
    kafka_streaming.send(KAFKA_TOPIC, key, value)
