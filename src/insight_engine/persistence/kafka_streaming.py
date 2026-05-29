import logging
from typing import Tuple

from confluent_kafka.avro import AvroProducer
from confluent_kafka.avro.cached_schema_registry_client import CachedSchemaRegistryClient

from insight_engine.config import ConfigLoader
from insight_engine.util.secrets import AbstractSecretManager

logger = logging.getLogger(__name__)


class KafkaStreaming:
    def __init__(self):
        self.producer = None
        self.schema_registry = None
        self.topic_prefix = ''
        self.produce_timeout_in_seconds = 0
        self.schema_by_subject = {}

    def setup(self, secrets_manager: AbstractSecretManager | None, producer=None, schema_registry=None):
        config = ConfigLoader.get_instance()
        fraudio_env_lowercase = config.fraudio_env.lower()
        kafka_env_lowercase = fraudio_env_lowercase if fraudio_env_lowercase in ['tst', 'prd'] else 'tst'
        self.topic_prefix = f'fraudio-{kafka_env_lowercase}-env.'
        self.produce_timeout_in_seconds = config.fraudio_kafka_producer_timeout_in_seconds
        if producer is not None and schema_registry is not None:
            self.producer = producer
            self.schema_registry = schema_registry
        else:
            schema_registry_url = config.fraudio_kafka_schema_registry_url.format(
                user=config.fraudio_kafka_schema_registry_user,
                pw=config.fraudio_kafka_schema_registry_pass
            )
            # See librdkafka for further configuration options
            self.schema_registry = CachedSchemaRegistryClient({
                'url': schema_registry_url,
                'auto.register.schemas': False
            })
            self.producer = AvroProducer({
                'bootstrap.servers': ','.join(config.fraudio_kafka_servers),
                'on_delivery': self._delivery_report,
                'security.protocol': 'SSL',
                'ssl.ca.location': secrets_manager.kafka_ca_cert_path(),
                'ssl.certificate.location': secrets_manager.kafka_api_cert_path(),
                'ssl.key.location': secrets_manager.kafka_api_key_path(),
            }, schema_registry=self.schema_registry)
        logger.info('Kafka producer is initialized.')

    def send_all(self, topic: str, events: list[Tuple[object, object]]):
        if self.producer is None or self.schema_registry is None:
            logger.debug('Message skipped: Kafka producer is not initialized.')
        else:
            logger.debug(f'Sending messages to topic {topic}')
            for (key, value) in events:
                self._produce(topic, key, value)
            self.producer.flush()

    def send(self, topic: str, key: str, message: str):
        if self.producer is None or self.schema_registry is None:
            logger.debug('Message skipped: Kafka producer is not initialized.')
        else:
            self._produce(topic, key, message)
            self.producer.flush()

    def _produce(self, topic: str, key: object, value: object):
        full_topic = self.topic_prefix + topic
        key_schema = self._get_schema(full_topic + '-key')
        value_schema = self._get_schema(full_topic + '-value')
        self.producer.produce(
            topic=full_topic,
            # Assume that the name of the schema subject is the topic name excluding the topic prefix
            key_schema=key_schema,
            value_schema=value_schema,
            key=key,
            value=value
        )

    def _get_schema(self, subject: str):
        if subject not in self.schema_by_subject:
            logger.debug(f'Fetching schema for subject {subject} from schema registry...')
            self.schema_by_subject[subject] = self.schema_registry.get_latest_schema(subject)[1]
            logger.debug(f'Fetched schema for subject {subject} from schema registry.')
        return self.schema_by_subject[subject]

    @staticmethod
    def _delivery_report(err, msg):
        if err is None:
            logger.debug(f'Kafka message delivered to {msg.topic()} [{(msg.partition())}]')
        else:
            logger.error(f'Kafka message delivery to {msg.topic()} failed: "{err}"')


kafka_streaming = KafkaStreaming()
