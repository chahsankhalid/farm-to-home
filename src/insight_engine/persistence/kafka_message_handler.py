import logging

from insight_engine.persistence.http_transaction_handler import (
    process_http_transactions_batch,
)

logger = logging.getLogger(__name__)


TOPIC_PROCESSORS = {
    '.http-transactions.v0':
        process_http_transactions_batch,
}


async def handle_kafka_message(
    topic: str,
    kafka_values: list[dict],
    kafka_headers: list[dict] | None = None
):
    for suffix, processor in (
        TOPIC_PROCESSORS.items()
    ):
        if topic.endswith(suffix):
            await processor(
                kafka_values
            )
            return

    logger.warning(
        f'No handler registered '
        f'for topic: {topic}'
    )