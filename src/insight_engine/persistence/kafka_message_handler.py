import json
import logging
import numpy as np

from insight_engine.model import model

logger = logging.getLogger(__name__)


async def handle_kafka_message(
    topic: str,
    kafka_values: list[dict],
    kafka_headers: list[dict] | None = None
):
    if topic.endswith('.raw-transactions.v0'):
        for transaction in kafka_values:
            try:
                request_body = transaction.get("requestBody")

                if not request_body:
                    logger.warning(
                        "No requestBody found in Kafka message"
                    )
                    continue

                payload = json.loads(request_body)

                features = payload.get("features")

                if not features:
                    logger.warning(
                        "No features found in payload"
                    )
                    continue

                arr = np.array(features).reshape(1, -1)

                prediction = int(model.predict(arr)[0])

                probability = (
                    float(max(model.predict_proba(arr)[0]))
                    if hasattr(model, "predict_proba")
                    else 0.0
                )

                logger.info(
                    f"Fraud prediction={prediction} "
                    f"probability={probability}"
                )

            except Exception as e:
                logger.exception(
                    f"Failed to process Kafka transaction: {e}"
                )

    else:
        logger.warning(
            f'No specific handler registered for topic: {topic}'
        )