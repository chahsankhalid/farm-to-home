import json
import logging
import threading
from confluent_kafka import Consumer

from insight_engine.config import ConfigLoader
from insight_engine.util.secrets import AbstractSecretManager

logger = logging.getLogger(__name__)


class KafkaConsumerService:
    def __init__(self):
        self.consumer = None
        self.running = False
        self.thread = None

    def setup(self, secrets_manager: AbstractSecretManager):
        config = ConfigLoader.get_instance()

        self.consumer = Consumer({
            'bootstrap.servers': ','.join(config.fraudio_kafka_servers),
            'group.id': 'insight-engine-consumer',
            'auto.offset.reset': 'earliest',
            'security.protocol': 'SSL',
            'ssl.ca.location': secrets_manager.kafka_ca_cert_path(),
            'ssl.certificate.location': secrets_manager.kafka_api_cert_path(),
            'ssl.key.location': secrets_manager.kafka_api_key_path(),
        })

        topic = 'fraudio-tst-env.fct.bronze.raw-transactions.v0'
        self.consumer.subscribe([topic])

        logger.info(f'Subscribed to Kafka topic: {topic}')

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._consume_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.consumer:
            self.consumer.close()

    def _consume_loop(self):
        logger.info('Kafka consumer started.')

        while self.running:
            msg = self.consumer.poll(1.0)

            if msg is None:
                continue

            if msg.error():
                logger.error(f'Kafka error: {msg.error()}')
                continue

            try:
                payload = json.loads(msg.value().decode('utf-8'))
                logger.info(f'Received raw transaction: {payload}')
            except Exception as e:
                logger.exception(f'Failed to process Kafka message: {e}')


kafka_consumer = KafkaConsumerService()