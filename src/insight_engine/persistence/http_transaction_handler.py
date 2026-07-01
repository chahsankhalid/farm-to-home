import json
import logging

from insight_engine.domain.models.http_transaction import (
    HttpTransaction,
)
from insight_engine.domain.payment_fraud_features import (
    build_payment_fraud_features,
)
from insight_engine.endpoints.predict import (
    predict,
)

logger = logging.getLogger(__name__)


async def process_http_transactions_batch(
    kafka_values: list[dict]
):
    """
    Batch orchestration:
    parse -> filter -> score
    """

    for transaction in kafka_values:
        try:
            http_transaction = (
                HttpTransaction
                .from_kafka_avro_dict(
                    transaction
                )
            )

            if (
                not http_transaction.request_headers
                or not http_transaction.request_body
            ):
                logger.warning(
                    "Missing requestHeaders "
                    "or requestBody"
                )
                continue

            raw_uri = (
                http_transaction
                .request_headers
                .get("Raw-Request-URI")
            )

            # Filter only payment scoring requests
            if raw_uri != "/payment-fraud-score":
                continue

            request_body = json.loads(
                http_transaction.request_body
            )

            await process_payment_fraud_score(
                request_body
            )

        except Exception as e:
            logger.exception(
                f"Failed processing Kafka "
                f"message: {e}"
            )


async def process_payment_fraud_score(
    request_body: dict
):
    """
    Score a payment fraud request.
    """

    arr = build_payment_fraud_features(
        request_body
    )

    prediction_result = predict(
        {
            "features": (
                arr.flatten().tolist()
            )
        }
    )

    logger.info(
        f"Prediction="
        f"{prediction_result['prediction']}, "
        f"probability="
        f"{prediction_result['probability']}"
    )